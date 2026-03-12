Here is a **cleaner, more readable version** with consistent formatting, spacing, and hierarchy. I grouped categories and fixed small wording/typo issues while keeping the same information.

---

# The Data

The dataset is a subset of the **Ames Housing Dataset**. Below are the variables included along with their descriptions.

---

## Property Classification

### **MS_SubClass** *(Nominal)*

The Assessor's office category of the type of dwelling involved in the sale.

### **MS_Zoning** *(Nominal)*

Identifies the general zoning classification of the sale.

| Code         | Description                                               |
| ------------ | --------------------------------------------------------- |
| A            | Agriculture                                               |
| F-PRD        | Floating Zone – Planned Residential                       |
| FV / F-VR    | Floating Zone – Village Residential                       |
| FS-RL / RM   | Floating Zone – Suburban Residential (Low/Medium Density) |
| UCRM         | Urban Core Residential Medium Density                     |
| GI / I(all)  | General Industrial Zone                                   |
| HOC          | Highway-Oriented Commercial Zone                          |
| NC / C(all)  | Neighborhood Commercial Zone                              |
| RH / RL / RM | Residential High / Low / Medium Density                   |
| S-SMD        | South-Lincoln Mixed Use District                          |

---

## Lot Information

### **Lot_Area** *(Continuous)*

Lot size in square feet.

---

## Building Characteristics

### **Bldg_Type** *(Nominal)*

Type of dwelling.

| Code           | Description                     |
| -------------- | ------------------------------- |
| 1FamDet        | One-family detached unit        |
| Twnhs-E / I    | Townhouse end / inside unit     |
| Condo          | Condominium                     |
| 2/3/4/5+FmConv | Converted multi-family dwelling |
| Duplex         | Duplex                          |

### **House_Style** *(Nominal)*

Style of dwelling.

| Code              | Description                                             |
| ----------------- | ------------------------------------------------------- |
| 1.5 Fin / 2.5 Fin | One or two-and-a-half story with finished upper level   |
| 1.5 Unf / 2.5 Unf | One or two-and-a-half story with unfinished upper level |
| 1-Story / 2-Story | One or two story building                               |
| S/Level           | Split level building                                    |
| S/Foyer           | Split foyer building                                    |

### **Year_Built** *(Discrete)*

Original construction year.

---

## Construction Materials

### **Roof_Matl** *(Nominal)*

Roof material.

| Code    | Description                 |
| ------- | --------------------------- |
| CompShg | Standard composite shingles |
| Tar&Grv | Gravel and tar              |
| WdShngl | Wood shingles               |
| WdShake | Wood shakes                 |
| Membran | Membrane                    |
| Metal   | Metal                       |
| ClyTile | Clay or tile                |

### **Exterior_1st** *(Nominal)*

Exterior covering of the house.

| Code    | Description       |
| ------- | ----------------- |
| VinylSd | Vinyl siding      |
| MetalSd | Metal siding      |
| Wd Sdng | Wood siding       |
| CemntBd | Cement board      |
| HdBoard | Hardboard         |
| BrkComm | Brick (common)    |
| PreCast | Precast           |
| Stucco  | Stucco            |
| WdShing | Wood shingles     |
| BrkFace | Brick face        |
| Plywood | Plywood           |
| AsbShng | Asbestos shingles |
| ImStucc | Imitation stucco  |
| AsphShn | Asphalt shingles  |
| CBlock  | Cinder block      |

### **Mas_Vnr_Type** *(Nominal)*

Masonry veneer type.

| Code    | Description  |
| ------- | ------------ |
| BrkFace | Brick face   |
| Stone   | Stone        |
| CBlock  | Cinder block |
| BrkCmn  | Brick common |

### **Foundation** *(Nominal)*

Type of foundation.

| Code   | Description     |
| ------ | --------------- |
| BrkTil | Brick and tile  |
| PConc  | Poured concrete |
| Slab   | Slab            |
| CBlock | Cinder block    |
| Stone  | Stone           |
| Wood   | Wood            |

---

## Basement Information

### **Total_Bsmt_SF** *(Continuous)*

Total basement area in square feet.

### **Bsmt_Fin_Pct** *(Proportion)*

Proportion of basement area that is fully finished.

### **Bsmt_Full_Bath** *(Discrete)*

Number of full bathrooms in the basement.

### **Bsmt_Half_Bath** *(Discrete)*

Number of half bathrooms in the basement.

---

## Heating and Cooling

### **Heating** *(Nominal)*

Type of heating system.

| Code     | Description                         |
| -------- | ----------------------------------- |
| GasA / W | Gas forced warm air / water heating |
| Grav     | Gravity furnace                     |
| OthA / W | Other warm air / water heating      |
| HeatPmp  | Heat pump                           |
| Wall     | Wall furnace                        |
| Floor    | Floor furnace                       |

### **Central_Air** *(Boolean)*

Indicates whether the house has central air conditioning (**Y / N**).

---

## Living Area

### **Gr_Liv_Area** *(Continuous)*

Above-grade living area (excluding basement) in square feet.

---

## Bathroom and Room Counts

| Variable      | Type     | Description                                   |
| ------------- | -------- | --------------------------------------------- |
| Full_Bath     | Discrete | Full bathrooms above grade                    |
| Half_Bath     | Discrete | Half bathrooms above grade                    |
| Bedroom_AbvGr | Discrete | Bedrooms above grade (excluding basement)     |
| TotRms_AbvGrd | Discrete | Total rooms above grade (excluding bathrooms) |

---

## Garage

### **Garage_Type** *(Nominal)*

Garage location/type.

| Code                | Description                 |
| ------------------- | --------------------------- |
| Attchd / Detchd     | Attached or detached garage |
| BuiltIn             | Built-in garage             |
| Basment             | Garage in basement          |
| CarPort             | Carport                     |
| More_Than_Two_Types | Multiple garage types       |

### **Garage_Cars** *(Discrete)*

Garage size measured in car capacity.

### **Garage_Area** *(Continuous)*

Garage area in square feet.

---

## Additional Features

| Variable   | Type       | Description              |
| ---------- | ---------- | ------------------------ |
| Fireplaces | Discrete   | Number of fireplaces     |
| Pool_Area  | Continuous | Pool area in square feet |

---

## Sale Information

| Variable  | Type     | Description      |
| --------- | -------- | ---------------- |
| Mo_Sold   | Discrete | Month sold (MM)  |
| Year_Sold | Discrete | Year sold (YYYY) |

### **Sale_Type** *(Nominal)*

Type of property sale.

| Code      | Description                        |
| --------- | ---------------------------------- |
| WRD / WRX | Warranty deed                      |
| Oth       | Other                              |
| Con       | Contract                           |
| COD       | Court officer deed or title change |
| New       | First transfer of the house        |

### **Sale_Price** *(Continuous)*

Final sale price (USD).