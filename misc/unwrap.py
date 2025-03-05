import numpy as np
def unwrap_phase_fft(wrapped):
    """
    Unwrap a 2D wrapped phase image using an FFT-based least-squares approach.
    
    The unwrapped phase φ_unwrapped at a pixel (i, j) can be thought
    of as the sum of the wrapped phase φ_wrapped at (i, j) plus an integer multiple of 2π that
    accounts for the cumulative phase differences (Δφ) between neighboring pixels:
    
       φ_unwrapped(i, j) = φ_wrapped(i, j) + 2π ∑ₖ₌₁ⁱ ∑ₗ₌₁ʲ Δφ(k, l)
    
    This function uses finite differences to compute the phase gradients (i.e. the phase differences 
    between neighboring pixels along the horizontal (x) and vertical (y) directions), constructs 
    the divergence of these differences, and then solves a Poisson equation using FFTs to recover 
    the unwrapped phase.

    The foundation for our FFT‑based least‑squares unwrapping function is conceptually based on the WDCT‑LS 
    (Weighted Discrete Cosine Transform Least‑Squares) method implemented in ISCE2. 
    In ISCE2, a similar approach is used to solve the Poisson equation for phase unwrapping, 
    integrating the finite differences (phase gradients) to obtain a continuous phase field.
    https://github.com/isce-framework/isce2/blob/main/contrib/UnwrapComp/phaseUnwrap.py
    Our function adapts this conceptual approach (computing finite differences, building the divergence, and solving via FFT) 
    in a simplified, standalone version for use directly on NumPy arrays and xarray DataArrays.
    
    Parameters
    ----------
    wrapped : 2D numpy array
        Wrapped phase in radians (ideally in the interval [-π, π], although your data might span 
        The array may contain NaNs
        
    Returns
    -------
    unwrapped : 2D numpy array
        Unwrapped phase in radians. This continuous phase field can then be converted to physical 
        displacement (e.g., using d = unwrapped_phase * (λ / (4π)) for a repeat-pass interferogram).
    """
    # -------------------------------------------------------------------------
    # 1. Ensure no NaNs are present.
    # NaNs will disrupt arithmetic and FFT computations
    # We replace them with the mean of the valid phase values so that the finite difference
    # calculations and the subsequent FFT do not propagate NaNs
    if np.isnan(wrapped).any():
        fill_value = np.nanmean(wrapped)  # get the mean of all valid (non-NaN) values.
        wrapped = np.where(np.isnan(wrapped), fill_value, wrapped)  # replace NaNs.
    
    # Get the dimensions of the input wrapped phase image.
    M, N = wrapped.shape

    # -------------------------------------------------------------------------
    # 2. Compute Finite Differences (Phase Gradients)
    # The finite difference along the horizontal direction (axis=1) computes the difference between
    # adjacent columns, representing the local phase change in the x-direction.
    # Similarly, the finite difference along the vertical direction (axis=0) computes differences
    # between adjacent rows, representing the local phase change in the y-direction.
    # These differences (dx and dy) form the discrete phase gradients that, when integrated,
    # reconstruct the continuous (unwrapped) phase.
    dx = np.diff(wrapped, axis=1)  # horizontal phase difference; shape becomes (M, N-1)
    dy = np.diff(wrapped, axis=0)  # vertical phase difference; shape becomes (M-1, N)

    # NOTE:
    # These finite differences are not the same as line-of-sight (LOS) deformation.
    # Rather, they are the differences in the measured (wrapped) phase between adjacent pixels.
    # LOS deformation is later derived from the unwrapped phase (using a conversion factor).

    # -------------------------------------------------------------------------
    # 3. Wrap the Finite Differences to the Interval [-π, π]
    # When computing differences, the raw subtraction might yield values outside the principal range.
    # The expression np.angle(np.exp(1j * value)) maps any phase difference back into the range [-π, π].
    # Even if your input wrapped phase spans [-2π, 2π], we want the differences to represent the
    # true smallest angular difference between pixels.
    dx = np.angle(np.exp(1j * dx))
    dy = np.angle(np.exp(1j * dy))

    # -------------------------------------------------------------------------
    # 4. Expand the Computed Differences Back to the Full Image Size
    # The np.diff function reduces the dimensions by one (since it computes differences between
    # adjacent pixels). To compute a divergence (which must have the same shape as the original image),
    # we "expand" (pad) these arrays back to size (M, N) by creating arrays of zeros and inserting the
    # computed finite differences into all positions where they are defined.
    # For dx, we fill columns 0 to N-2, leaving the last column as 0.
    # For dy, we fill rows 0 to M-2, leaving the last row as 0.
    dx_full = np.zeros((M, N), dtype=wrapped.dtype)
    dy_full = np.zeros((M, N), dtype=wrapped.dtype)
    dx_full[:, :-1] = dx
    dy_full[:-1, :] = dy

    # -------------------------------------------------------------------------
    # 5. Build the Divergence (Right-Hand Side of the Poisson Equation)
    # The divergence of the phase gradient field is the net "flow" of phase difference out of each pixel.
    # In our discrete formulation, we compute it by taking differences of the finite differences.
    # For the x-component, the divergence at column 0 is simply the first finite difference, and for
    # subsequent columns, it is the difference between adjacent values of dx_full.
    # Similarly for the y-component.
    rhs = np.zeros((M, N), dtype=wrapped.dtype)
    # Compute x divergence:
    rhs[:, 0] = dx_full[:, 0]                   # The first column (no left neighbor exists).
    rhs[:, 1:] = dx_full[:, 1:] - dx_full[:, :-1] # Difference between consecutive horizontal differences.
    # Compute y divergence:
    rhs[0, :] += dy_full[0, :]                  # The first row (no upper neighbor exists).
    rhs[1:, :] += dy_full[1:, :] - dy_full[:-1, :]# Difference between consecutive vertical differences.

    # This divergence corresponds to the accumulated difference between the wrapped phase gradients
    # and what would be the true (unwrapped) phase gradients, integrated over the image.

    # -------------------------------------------------------------------------
    # 6. Solve the Poisson Equation Using FFT
    # The Poisson equation in this context is: ∇² φ_unwrapped = divergence, where the divergence (rhs)\n",
    # represents the difference between the measured (wrapped) gradients and the true gradients.
    # By taking the FFT of both sides, the Laplacian operator becomes a multiplication in the frequency domain.
    fft_rhs = np.fft.fft2(rhs)  # Compute the 2D FFT of the divergence field.
    
    # Generate frequency grids for the two dimensions.
    # np.fft.fftfreq returns frequencies in cycles per pixel, and multiplying by 2π converts to radians.
    x_freq = np.fft.fftfreq(N) * 2 * np.pi
    y_freq = np.fft.fftfreq(M) * 2 * np.pi
    # Create a 2D meshgrid of frequencies; note 'ij' indexing to match array dimensions.
    Y, X = np.meshgrid(y_freq, x_freq, indexing='ij')
    
    # The denominator corresponds to the eigenvalues of the discrete Laplacian operator:
    # For a pixel grid, the Laplacian eigenvalues are: 2*cos(X) + 2*cos(Y) - 4.
    # We rearrange it as: (2*cos(X) - 2) + (2*cos(Y) - 2).
    denom = (2 * np.cos(X) - 2) + (2 * np.cos(Y) - 2)
    # Set the zero-frequency (DC) component to 1 to avoid division by zero.
    # This component represents the overall mean of the solution, which is undetermined
    # We will later set it explicitly to 0 to fix the arbitrary constant in phase
    denom[0, 0] = 1.0
    
    # Divide the FFT of the divergence by the eigenvalue spectrum to get the FFT of the unwrapped phase.
    fft_phi = fft_rhs / denom
    # Set the DC component (mean value) of the unwrapped phase to 0, since absolute phase is ambiguous
    fft_phi[0, 0] = 0.0
    
    # Invert the FFT to transform back to the spatial domain, yielding the unwrapped phase map.
    # The real part is taken because the imaginary part should be negligible (numerical noise).
    unwrapped = np.real(np.fft.ifft2(fft_phi))
    
    # The resulting 'unwrapped' phase is now a continuous field (in radians) that can be used to derive
    # physical displacement measurements (e.g., via d = unwrapped * (λ/(4π)))
    return unwrapped