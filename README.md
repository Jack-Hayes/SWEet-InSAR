# SWEet-InSAR
# ❄️🌨️ **Snow Water Equivalent Estimation via Sentinel-1 InSAR** 🌨️❄️

Snow Hydrology (CEWA 568) Winter 2025 Final Project

## **Project Team**  
- **Jack Hayes** ([@Jack-Hayes](https://github.com/jack-hayes))  
- **Collaborators:** (this could be you!)

---

## **Overview**  
**SWEet-InSAR** explores the power of **Sentinel-1 C-band InSAR** to estimate **snow water equivalent (SWE)** in mountainous regions. With climate change altering water resource patterns in the **Western United States**, accurately predicting snowmelt runoff volume is crucial for managing **water storage**, **flooding risks**, and **agriculture**. This project leverages Sentinel-1 C-band radar data to better understand a potentially scalable and cost-effective method for monitoring SWE over large areas.

Here, we focus on a singular pair of ascending and descending Sentinel-1 bursts over the San Juan National Forest in western Colorado. This limited selection is due to the limited project scope of a quarter system course. We chose Colorado as we believe the drier snowpack will allow for more-accurate estimations from SAR. We hope to address the question: Can Sentinel-1 C-band InSAR be used to retrieve meaningful SWE estimates in regions with dry snowpack?

This approach is inspired by **Tarricone et al. (2023)** which utilized UAVSAR L-band to measure snowpack characteristics. However, UAVSAR flights are **expensive** and **spatially and temporally sparse**, which motivates the use of Sentinel-1 to provide more frequent, global coverage. Will NISAR be better for this and is this a waster of time in terms of scientific contribution? Absolutely, but I need a final project.

---

## **Problem Statement**  
Accurately predicting snowmelt timing and SWE is essential for managing water storage, flooding risks, and agricultural needs in regions that rely heavily on snowmelt runoff. However, traditional snow monitoring methods such as manual snow surveys are time-consuming, labor-intensive, and limited in spatial coverage, especially in remote or inaccessible areas.

Radar-based techniques, such as Interferometric Synthetic Aperture Radar (InSAR), offer an attractive alternative by enabling large-area monitoring without being constrained by terrain accessibility or seasonal changes. Radar signals interact with the snowpack's dielectric properties (how the material affects electromagnetic wave propagation), which is telling of the water contents and structure of a snowpack. This interaction is key for estimating SWE, as the radar signal’s phase shift and amplitude will change based on the snowpack's structure and water content.

UAVSAR L-band radar has been shown to be effective for snowpack monitoring, due to its ability to penetrate snow and measure deeper snow layers. However, UAVSAR flights are expensive, have limited spatial coverage, and can be temporally sparse, making them unsuitable for long-term, large-scale monitoring. This project aims to explore the potential of Sentinel-1 C-band InSAR as a more accessible and frequent alternative. C-band radar is less penetrating than L-band but still sensitive to surface snowpack characteristics, potentially offering a cost-effective solution for monitoring snowmelt in a scalable way.

---

## **Background**  
Synthetic Aperture Radar (SAR) is a remote sensing technology that uses radar waves to capture high-resolution images of the Earth's surface. Unlike optical imagery, SAR operates in the microwave spectrum and can penetrate clouds and work in all weather conditions, making it an ideal tool for monitoring snow-covered regions. InSAR (Interferometric Synthetic Aperture Radar) is a technique that uses pairs of SAR images to measure small changes in surface elevation by comparing the phase difference between the two radar signals. These phase shifts can be used to derive information about the surface deformation or structural changes over time.

When radar waves interact with the snow surface, they are reflected back to the sensor, and their behavior is influenced by the snow's dielectric properties—its density, moisture content, and internal structure. These properties determine how well the radar waves penetrate the snowpack and how much of the signal is reflected back to the sensor. The amount of reflection can be correlated with snow depth and water content, which are key factors in estimating SWE.

Despite the potential for Sentinel-1 to monitor snowpack surface dynamics and snowmelt timing, its use for accurate SWE estimation has been limited. One major challenge is the difficulty in separating snowpack surface roughness from the snow's moisture content, as both factors influence the radar signal. Additionally, since C-band radar is more sensitive to surface features than L-band (such as that used by UAVSAR), its ability to detect subtle changes in snowpack water content, especially in dense or wet snow, is often hindered. Moreover, the complex terrain of mountainous regions, which frequently hosts snow-covered surfaces, can distort radar signals and introduce errors into measurements. The absence of well-established algorithms for directly linking C-band radar data to SWE is another barrier to using this technology for large-scale, accurate snowmelt prediction.

Ultimately, while C-band InSAR has shown promise for snow monitoring, it is not yet a widely adopted tool for SWE estimation due to these challenges in reliably interpreting the radar signals in the context of snowpack properties. This research aims to explore the capabilities of Sentinel-1 C-band InSAR as a cost-effective and scalable alternative to current snow monitoring techniques, with a focus on overcoming the limitations of surface sensitivity and terrain distortion.

---

## **Datasets**  
To evaluate the effectiveness of **Sentinel-1 InSAR** for snowmelt estimation, we will use the following datasets:
- **[Sentinel-1](https://sentinel.esa.int/web/sentinel/home)** – C-band radar phase information
  - Still debating whether to use NASA OPERA CSLC or standard Sentinel-1 SLCs... less support for OPERA CSLC INSAR processing
- **[SNOTEL (SWE)](https://www.nrcs.usda.gov/wps/portal/wcc/home/aboutUs/monitoringPrograms/automatedSnowMonitoring/)** – "Ground-truth" SWE measurements from SNOTEL snow monitoring stations in the U.S.

---

## **Methodology**  

### **Data Acquisition & Preprocessing**  
✅ Obtain **SNOTEL data** from the [USDA](https://www.nrcs.usda.gov/wps/portal/wcc/home/aboutUs/monitoringPrograms/automatedSnowMonitoring/)
✅ Obtain **Sentinel-1 CSLC (Coregistered Single Look Complex) data** from NASA's [OPERA Coregistered SLC](https://www.jpl.nasa.gov/go/opera)
✅ Obtain corresponding **Copernicus GLO-30 Digital Elevation Model data** (https://portal.opentopography.org/raster?opentopoID=OTSDEM.032021.4326.3) and spatially align with respective CSLC data

### **Topographic Phase Removal**  
- Use the **COP 30 DEM** to subtract the topographic contribution from the interferometric phase.  

### **Phase Unwrapping**  
- Unwrap the interferometric phase to retrieve continuous surface displacement values.  

### **Validation with SNOTEL Data**  
- Compare interferometric phase differences with SNOTEL station SWE measurements to assess accuracy.  
- Investigate discrepancies and evaluate potential error sources, including atmospheric effects, surface roughness, and temporal decorrelation.  

### **Interpretation & Discussion**  
- Compare results with existing studies that have used L-band UAVSAR for SWE estimation.  

---

## **Tools & Software**  
- Still deciding on best options for InSAR processing...

---

## **Related Work**  
- **[Estimating Snow Accumulation and Ablation with L-Band InSAR (Tarricone et al., 2023)](https://tc.copernicus.org/articles/17/1997/2023/tc-17-1997-2023-discussion.html)** – Paper discussing **L-band radar** for estimating snow accumulation and ablation and its limitations.

---

## **References**  
- **Tarricone, J., Webb, R. W., Marshall, H.-P., Nolin, A. W., & Meyer, F. J. (2023).** *Estimating snow accumulation and ablation with L-band interferometric synthetic aperture radar (InSAR).* The Cryosphere, 17(1997-2023). [Link](https://tc.copernicus.org/articles/17/1997/2023/tc-17-1997-2023-discussion.html)  
