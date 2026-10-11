import streamlit as st
import pandas as pd
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Furniture Sketch AI", page_icon="📐", layout="wide")

st.title("Furniture Sketch AI")
st.caption("Početni prototip za provjeru dimenzija ormara i izradu liste za rezanje.")
st.info(
    "Ova verzija još ne prepoznaje dimenzije automatski sa slike. "
    "Ubaci skicu, unesi dimenzije i provjeri rezultate. Kasnije možemo dodati OCR i AI model."
)

with st.sidebar:
    st.header("Postavke projekta")
    project_name = st.text_input("Naziv projekta", "Moj ormar")
    unit = st.selectbox("Jedinica", ["mm", "cm"], index=0)
    st.caption("Unosi sve dimenzije u odabranoj jedinici.")

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("1. Skica")
    uploaded = st.file_uploader(
        "Ubaci fotografiju ili sliku crteža",
        type=["png", "jpg", "jpeg", "webp"]
    )
    if uploaded:
        try:
            image = Image.open(uploaded)
            st.image(image, caption="Učitana skica", use_container_width=True)
        except Exception:
            st.error("Ne mogu otvoriti ovu sliku. Probaj PNG ili JPG datoteku.")
    else:
        st.write("Ovdje će se prikazati tvoja skica.")

    st.subheader("2. Vanjske dimenzije")
    width = st.number_input(f"Širina ormara ({unit})", min_value=1.0, value=800.0, step=10.0)
    height = st.number_input(f"Visina ormara ({unit})", min_value=1.0, value=2000.0, step=10.0)
    depth = st.number_input(f"Dubina ormara ({unit})", min_value=1.0, value=600.0, step=10.0)
    thickness = st.number_input(f"Debljina ploče ({unit})", min_value=1.0, value=18.0, step=1.0)
    shelves = st.number_input("Broj unutrašnjih polica", min_value=0, max_value=30, value=3, step=1)

with right:
    st.subheader("3. Rezultati provjere")
    issues = []
    if thickness * 2 >= width:
        issues.append("Debljina dvije bočne ploče je jednaka ili veća od ukupne širine.")
    if thickness * 2 >= height:
        issues.append("Debljina gornje i donje ploče je jednaka ili veća od ukupne visine.")
    if thickness >= depth:
        issues.append("Debljina ploče je jednaka ili veća od dubine ormara.")
    if width <= 0 or height <= 0 or depth <= 0 or thickness <= 0:
        issues.append("Sve dimenzije moraju biti veće od nule.")

    inner_width = width - 2 * thickness
    inner_height = height - 2 * thickness
    inner_depth = depth - thickness

    if inner_width > 0 and inner_depth > 0 and inner_height > 0:
        shelf_width = inner_width
        shelf_depth = inner_depth
        usable_height = inner_height
    else:
        shelf_width = shelf_depth = usable_height = 0

    if issues:
        st.error("Pronađene moguće greške")
        for issue in issues:
            st.write(f"• {issue}")
    else:
        st.success("Osnovne dimenzije su matematički moguće.")
        st.caption("Ovo nije potpuna provjera konstrukcije ili sigurnosti namještaja.")

    st.metric("Unutrašnja širina", f"{inner_width:.1f} {unit}" if inner_width > 0 else "Provjeri dimenzije")
    st.metric("Unutrašnja visina", f"{inner_height:.1f} {unit}" if inner_height > 0 else "Provjeri dimenzije")
    st.metric("Procijenjena unutrašnja dubina", f"{inner_depth:.1f} {unit}" if inner_depth > 0 else "Provjeri dimenzije")

    if shelves > 0 and usable_height > 0:
        clear_gap = (usable_height - shelves * thickness) / (shelves + 1)
        if clear_gap < 0:
            st.warning("Police i razmaci ne staju u raspoloživu visinu prema ovom jednostavnom modelu.")
        else:
            st.write(f"Približan jednak razmak između polica: **{clear_gap:.1f} {unit}**")
    else:
        clear_gap = None

st.divider()
st.subheader("4. Početna lista za rezanje")
st.caption(
    "Pretpostavka: jednostavan pravougaoni ormar s dvije bočne stranice, "
    "gornjom i donjom pločom te policama. Ne uključuje leđa, vrata, kantovanje, "
    "spojeve, zazore ni optimizaciju rasporeda na ploči."
)

cut_rows = [
    {"Dio": "Bočna stranica", "Količina": 2, f"Širina ({unit})": height, f"Dužina ({unit})": depth},
    {"Dio": "Gornja ploča", "Količina": 1, f"Širina ({unit})": inner_width, f"Dužina ({unit})": depth},
    {"Dio": "Donja ploča", "Količina": 1, f"Širina ({unit})": inner_width, f"Dužina ({unit})": depth},
]
if shelves > 0:
    cut_rows.append({"Dio": "Polica", "Količina": int(shelves), f"Širina ({unit})": shelf_width, f"Dužina ({unit})": shelf_depth})

cut_df = pd.DataFrame(cut_rows)
st.dataframe(cut_df, use_container_width=True, hide_index=True)

csv_data = cut_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "Preuzmi listu za rezanje (CSV)",
    data=csv_data,
    file_name="lista_za_rezanje.csv",
    mime="text/csv"
)

st.divider()
st.subheader("Šta još treba dodati")
st.write(
    "• Automatsko prepoznavanje brojeva i dimenzija sa skice\n"
    "• Provjera sudara u pravom 3D modelu\n"
    "• Uzimanje u obzir vrata, leđa, spojeva i zazora\n"
    "• Optimizacija rezanja i procjena otpada\n"
    "• Testiranje na označenim skicama i dodavanje treniranog modela"
)
st.caption("Prototip služi za učenje i testiranje. Prije rezanja materijala obavezno ručno provjeri mjere.")
