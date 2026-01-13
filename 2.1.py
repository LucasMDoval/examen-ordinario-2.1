import os
import xarray as xr
import matplotlib.pyplot as plt

# -------------------------
# Rutas relativas (GitHub-friendly)
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NC_PATH = os.path.join(BASE_DIR, "ERA5_LAND_2mT_TMax_dailyvalue_EU_2022-10.nc")

OUT_DIR = os.path.join(BASE_DIR, "salida")
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PNG = os.path.join(OUT_DIR, "mapa_area_4a22C_Tmax_media_2022-10-05_06.png")

# -------------------------
# Parámetros
# -------------------------
LAT_N, LAT_S = 72.0, 36.0
LON_W, LON_E = -25.0, 30.0

START = "2022-10-05"
END   = "2022-10-06"

TMIN, TMAX = 4.0, 22.0

# =========================
# RESPUESTAS (a) y (b) (resultado esperado con este dataset + recorte)
# (a) Tmax_2d_max ≈ 32.87 ºC en lat ≈ 38.90º, lon ≈ -6.70º
# (b) Mapa guardado en: salida/mapa_area_4a22C_Tmax_media_2022-10-05_06.png
# =========================

# -------------------------
# Cálculo
# -------------------------
ds = xr.open_dataset(NC_PATH)

t2m = ds["t2m"]  # Kelvin
t_two_days = t2m.sel(time=slice(START, END))
t_two_days_c = t_two_days - 273.15  # ºC

tmean2 = t_two_days_c.mean("time")
tmean2_eu = tmean2.sel(latitude=slice(LAT_N, LAT_S), longitude=slice(LON_W, LON_E))

# (a) Máximo + localización
max_temp = float(tmean2_eu.max().values)
stacked = tmean2_eu.stack(z=("latitude", "longitude"))
idx = int(stacked.argmax("z").values)
latmax = float(stacked["latitude"].isel(z=idx).values)
lonmax = float(stacked["longitude"].isel(z=idx).values)

print("Periodo analizado:", START, "y", END)
print("Recorte Europa: lat", LAT_S, "–", LAT_N, "N ; lon", LON_W, "–", LON_E, "E")
print("(a) Tmax_2d_max (máximo espacial de la Tmax media 2 días): {:.2f} ºC".format(max_temp))
print("    Localización aprox del máximo: lat {:.2f}º, lon {:.2f}º".format(latmax, lonmax))
print()

# (b) Mapa 4–22 ºC
mask = (tmean2_eu >= TMIN) & (tmean2_eu <= TMAX)
t_in_range = tmean2_eu.where(mask)

lons = t_in_range["longitude"].values
lats = t_in_range["latitude"].values
Z = t_in_range.values

plt.figure(figsize=(10, 6))
pc = plt.pcolormesh(lons, lats, Z, shading="auto")
plt.colorbar(pc, label=f"Tmax media {START}–{END} (ºC) [solo {TMIN}–{TMAX} ºC]")
plt.title(f"Área con Tmax media ({START}–{END}) entre {TMIN} y {TMAX} ºC (ERA5-Land)")
plt.xlabel("Longitud (º)")
plt.ylabel("Latitud (º)")
plt.tight_layout()
plt.savefig(OUT_PNG, dpi=200)
plt.show()

print("(b) Mapa guardado en:", OUT_PNG)

ds.close()
