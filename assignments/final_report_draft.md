# Estimating Snow Water Equivalent using Sentinel‑1 C‑Band InSAR  
*Preliminary Report for Snow Hydrology Final Project*

---

## Abstract

Accurate estimation of snow water equivalent (SWE) is critical for water resource management, flood mitigation, and agricultural planning in regions reliant on snowmelt runoff. Here, we explore the feasibility of using Sentinel‑1 C‑band Interferometric Synthetic Aperture Radar (InSAR) to infer SWE in the San Juan National Forest, western Colorado. Although previous work (e.g., Tarricone et al., 2023) has demonstrated the effectiveness of L‑band InSAR for snow monitoring, the inherent limitations of C‑band radar in penetrating snow raise significant challenges. Building on foundational principles from *Introduction to Microwave Remote Sensing* (Woodhouse) regarding microwave–dielectric interactions in snow, we evaluate whether C‑band InSAR can yield meaningful SWE estimates in regions with predominantly dry snowpack. Our analysis incorporates corrections for topographic, atmospheric, orbital, and noise contributions to the radar phase and employs FFT‑based phase unwrapping techniques to derive surface displacements, which are then projected into vertical motion. The preliminary results indicate considerable uncertainties, highlighting the need for further refinement in methodology and data fusion with other sensors.

---

## 1. Introduction

### 1.1 Background

Estimating Snow Water Equivalent (SWE) is essential for water resource management, as it quantifies the water stored in snowpacks, which contributes to river flows and groundwater recharge upon melting. Accurate SWE measurements improve water availability forecasts, informing agricultural planning, hydroelectric power generation, and municipal water supplies. Spaceborne remote sensing has the potential to provide extensive spatial coverage for accurate SWE estimation, enabling consistent monitoring of remote mountainous regions that are otherwise difficult to access. Among remote sensing technologies, Synthetic Aperture Radar (SAR) is particularly useful for observing snow properties over large areas.

Traditionally, SAR backscatter techniques have been used to assess snow properties, particularly wetness, by detecting decreases in backscatter intensity as wet snow attenuates radar signals. However, estimating SWE using backscatter methods—especially at shorter wavelengths such as Ku- and X-band—requires complex dense-media radiative transfer models. An alternative approach is Interferometric SAR (InSAR), which relates changes in interferometric phase to variations in SWE under dry snow conditions. By leveraging phase information from multiple SAR acquisitions, InSAR detects subtle surface displacements caused by snow accumulation or melt, offering a potentially more direct and less parameter-intensive means of SWE estimation. Although radiative transfer corrections in our dataset make backscatter analysis a viable option, we pursued InSAR processing to explore its potential for SWE retrieval (Truly, the products we're using provide enough radiative transfer correction and backscatter analysis would likely be better, but I wanted to learn InSAR processing).

The fundamental principle underlying InSAR is that the radar phase encodes the path length between the satellite and the ground surface. For a pair of SAR acquisitions, the observed phase is a combination of several contributions:

$$
\varphi = W \left( \varphi_{\text{topography}} + \varphi_{\text{deformation}} + \varphi_{\text{atmosphere}} + \varphi_{\text{orbit}} + \varphi_{\text{noise}} \right)
$$

where $W$ is the wrap operator confining the phase to \([-π, π]\).

The interaction of microwaves with snow is largely governed by the dielectric properties of the snowpack. According to Woodhouse in *Introduction to Microwave Remote Sensing*, the dielectric constant of snow depends on factors such as density, water content, and grain size. These properties determine the degree to which microwaves are absorbed or reflected, thereby influencing the InSAR signal. While L‑band radar can penetrate deeper into the snowpack and provide reliable information about its internal structure, C‑band radar is more sensitive to surface properties. This sensitivity, combined with the complexities of mountainous terrain, poses significant challenges for accurately estimating SWE using C‑band data.

### 1.2 Research Question

Given the technical constraints of C‑band spaceborne InSAR and the complex interaction of microwaves with snow, our study is guided by the following research question:

**Can Sentinel‑1 C‑band InSAR be effectively utilized to retrieve meaningful SWE estimates in regions characterized by dry snowpack, despite its inherent limitations compared to L‑band systems?**

---

## 2. Methods

### 2.1 Data Acquisition and Preprocessing

The primary datasets used in this study are:
- **Sentinel‑1 C‑band CSLC Data:** Acquired over the San Juan National Forest, these datasets provide the interferometric phase information necessary for surface displacement analysis.
- **SNOTEL SWE Measurements:** Ground‐truth SWE data from SNOTEL stations are employed for validation of the derived displacement and SWE estimates.

The Sentinel‑1 data have been preprocessed using NASA OPERA CSLC products, which include rigorous corrections for orbital inaccuracies, topographic effects, and atmospheric delays. The pre‐flattening step removes the flat‐Earth and topographic contributions via a reference Digital Elevation Model (DEM), specifically the Copernicus GLO‑30 DEM.

### 2.2 Theoretical Framework

#### 2.2.1 Phase Contributions and Correction

The interferometric phase, as observed in our data, comprises multiple components. The most significant contributions include:

- **Topographic Phase $$\varphi_{\text{topography}}$$**  
  Variations in surface elevation cause differences in radar path lengths. This phase is approximated by:

$$ \varphi_{\text{topography}} = \frac{4\pi B h}{\lambda R \sin(\theta)} $$

  where:

  - $\lambda$ is the radar wavelength,
  - $B$ is the baseline (separation between acquisitions),
  - $h$ is the surface elevation from the DEM,
  - $R$ is the radar line‑of‑sight distance,
  - $\theta$ is the incidence angle.

- **Atmospheric Phase $$\varphi_{\text{atmosphere}}$$**  
  Fluctuations in atmospheric conditions (temperature, pressure, and water vapor) introduce phase delays that must be corrected for accurate displacement estimation.

- **Orbital and Noise Phases $$\varphi_{\text{orbit}}$$ and $$\varphi_{\text{noise}}$$**  
  Although typically minor relative to the other terms, these are also considered in our processing pipeline.

#### 2.2.2 Phase Unwrapping and Displacement Calculation

In order to interpret the wrapped phase data, an FFT‑based least‑squares phase unwrapping technique is utilized. The unwrapped phase is computed as:

$$
\phi_{\text{unwrapped}}(i,j) = \phi_{\text{wrapped}}(i,j) + 2\pi \sum_{k=1}^{i} \sum_{l=1}^{j} \Delta\phi(k,l)
$$

where $\Delta\phi(k,l)$ represents the phase difference between adjacent pixels.

Conversion of the unwrapped phase to physical displacement is accomplished by the relationship:

$$
d = \Delta\phi \frac{\lambda}{4\pi}
$$

with $d$ representing the line‑of‑sight (LOS) displacement. Given that the radar signal primarily measures displacement along the LOS, a geometric projection is required to infer vertical (up/down) displacement:

$$
d_{\text{vertical}} = \frac{d_{\text{LOS}}}{\cos(\theta)}
$$

This vertical displacement is then analyzed in the context of SWE, as variations in the snowpack’s dielectric properties alter the radar backscatter and phase response.

#### 2.2.3 Microwave–Snow Interaction

The dielectric properties of snow play a crucial role in determining the radar signal response. Woodhouse’s *Introduction to Microwave Remote Sensing* explains that snow’s dielectric constant increases with water content, influencing both the attenuation and phase of the microwave signal. The sensitivity of C‑band radar to these changes is, however, limited compared to L‑band systems, which can penetrate deeper into the snowpack and provide more accurate SWE estimations.

For Sentinel‑1, which operates at a C‑band wavelength of approximately 5.6 cm, the interaction with a dry snowpack is dominated by surface scattering phenomena. Dry snow typically exhibits a low dielectric constant (on the order of 1.2–1.5) due to its high air content. At this wavelength, the radar signal’s penetration is constrained primarily to the uppermost layers of the snowpack. The physical scale of 5.6 cm is relatively long compared to the size of individual snow grains, but the snowpack’s microstructure—characterized by grain boundaries, layering, and potential stratification—can still induce multiple scattering events and phase distortions.

Because the electromagnetic radiation is primarily sensitive to the top few centimeters, there is a limitation in capturing the full vertical profile of the snowpack, potentially leading to underestimation of SWE when significant subsurface moisture gradients are present. In our context, where the snowpack is predominantly dry, the radar signal predominantly reflects off the surface, and the phase response is modulated by minor surface variations rather than by the integrated properties of the entire snowpack.

Additionally, as the snow begins to melt, even slight increases in liquid water content result in a marked increase in the dielectric constant, which in turn enhances signal attenuation and further alters the phase response. This transition from dry to wet snow introduces complexities in isolating the contribution from surface displacement related solely to snowmelt.

Understanding these interactions is critical for calibrating our InSAR-derived displacement measurements to SWE. The challenge lies in disentangling the contributions of surface roughness, snow layering, and melt-induced changes from the true deformation signal. Future work may benefit from coupling C‑band measurements with auxiliary data or adopting multi-frequency approaches to better characterize the full snowpack structure.


### 2.3 Data Analysis Techniques



---

## 3. Results

The preliminary analysis indicates that the derived displacement maps exhibit the expected phase shifts corresponding to snowmelt and accumulation events. However, due to the limitations of C‑band radar—namely its sensitivity primarily to surface scattering—the correlation between vertical displacement and SWE is weaker than anticipated. In regions with a predominantly dry snowpack, the radar signal reflects more prominently from the surface, resulting in a lower sensitivity to subsurface moisture variations.

---

## 4. Discussion

The study demonstrates that while Sentinel‑1 C‑band InSAR offers a cost‑effective and frequent data source, its utility in accurately estimating SWE is hampered by several factors:
- **Limited Penetration Depth:** The C‑band radar’s sensitivity due to its shorter wavelength reduces its capability to capture subsurface moisture variations.
- **Complex Terrain Effects:** Mountainous regions and dense vegetation introduce geometric distortions and residual phase errors that further confound the SWE estimation.
- **Assumptions in Geometric Projection:** The projection from LOS to vertical displacement assumes minimal horizontal motion—a condition that may not always hold true in dynamic snowpack environments, especially blowing snow events.

Comparatively, Tarricone et al. (2023) employed L‑band InSAR, which benefits from greater penetration capabilities and more robust sensitivity to internal snowpack properties. The findings of our study, therefore, highlight the trade-offs between radar frequency, spatial resolution, and penetration depth in the context of snow hydrology.

### 4.1 Future Research Directions

Future work should consider:
- **Multi‑Frequency Approaches:** Integrating C‑band with L‑band or even X‑band data to leverage the strengths of each frequency.
- **Enhanced Modeling:** Coupling InSAR data with physical snowpack models may improve the SWE estimation by incorporating additional variables such as temperature gradients and density profiles.

---

## 5. Conclusions


---

## References

1. **Woodhouse, I. H.** *Introduction to Microwave Remote Sensing*. This text provides a fundamental understanding of microwave interactions with natural surfaces, including the dielectric properties of snow.
2. **Tarricone, J., Webb, R. W., Marshall, H.-P., Nolin, A. W., & Meyer, F. J.** (2023). Estimating snow accumulation and ablation with L‑band interferometric synthetic aperture radar (InSAR). *The Cryosphere, 17*(1997-2023).  
3. **Ferretti, A., Prati, C., & Rocca, F.** (2001). InSAR processing: Techniques and challenges in phase unwrapping and correction. *IEEE Transactions on Geoscience and Remote Sensing*.
