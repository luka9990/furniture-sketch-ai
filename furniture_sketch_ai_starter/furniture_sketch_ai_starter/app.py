import streamlit as st
import pandas as pd
from PIL import Image

st.set_page_config(page_title="Furniture Sketch AI #0.1", page_icon="📐", layout="wide")
st.title("Furniture Sketch AI")
st.caption("Verzija #0.1 — ručni parametri, kolone i zasebni razmaci između polica.")
st.info("Ova verzija ne koristi AI i ne prepoznaje dimenzije sa skice. Rezultati su preliminarni; provjeri konstrukciju i mjere prije rezanja materijala.")

# Stable IDs keep widget values associated with the correct column when one is removed.
if "columns_data" not in st.session_state:
    st.session_state.columns_data = [
        {"id": 1, "name": "Kolona 1", "width": 400.0, "shelves": 2}
    ]
if "next_column_id" not in st.session_state:
    st.session_state.next_column_id = 2

with st.sidebar:
    st.header("Projekat")
    project_name = st.text_input("Naziv projekta", "Moj namještaj")
    furniture_type = st.selectbox("Vrsta namještaja", ["Ormar", "Polica / regal", "Komoda", "Kuhinjski element", "Sto", "Drugo"])
    unit = st.selectbox("Jedinica za dimenzije", ["mm", "cm"], index=0)
    st.caption("Za police i kolone sve dimenzije moraju koristiti istu jedinicu.")

factor = 1.0 if unit == "mm" else 10.0

left, right = st.columns([1, 1], gap="large")
with left:
    st.subheader("1. Skica (opcionalno)")
    uploaded = st.file_uploader("Ubaci sliku crteža", type=["png", "jpg", "jpeg", "webp"])
    if uploaded:
        try:
            image = Image.open(uploaded)
            st.image(image, caption="Učitana skica", use_container_width=True)
        except Exception:
            st.error("Ne mogu otvoriti ovu sliku. Probaj PNG ili JPG.")
    st.subheader("2. Vanjske dimenzije")
    width = st.number_input(f"Ukupna vanjska širina ({unit})", min_value=1.0, value=1200.0, step=10.0)
    height = st.number_input(f"Vanjska visina ({unit})", min_value=1.0, value=2000.0, step=10.0)
    depth = st.number_input(f"Vanjska dubina ({unit})", min_value=1.0, value=600.0, step=10.0)
    thickness = st.number_input(f"Debljina ploče ({unit})", min_value=1.0, value=18.0 if unit == "mm" else 1.8, step=1.0 if unit == "mm" else 0.1)
    st.caption("Širina svake kolone ispod predstavlja čistu unutrašnju širinu prostora između pregrada.")

st.divider()
st.subheader("3. Kolone i raspored polica")
st.write("Dodaj kolone, promijeni njihove širine i broj polica. Svaka kolona ima vlastite razmake; kolonu možeš ukloniti ako je greškom dodana.")

cols = st.session_state.columns_data
add_col, reset_col = st.columns([1, 1])
with add_col:
    if st.button("➕ Dodaj kolonu", use_container_width=True):
        cid = st.session_state.next_column_id
        st.session_state.next_column_id += 1
        st.session_state.columns_data.append({"id": cid, "name": f"Kolona {cid}", "width": 300.0, "shelves": 2})
        st.rerun()
with reset_col:
    if st.button("↩️ Vrati na jednu kolonu", use_container_width=True):
        first = st.session_state.columns_data[0] if st.session_state.columns_data else {"id": st.session_state.next_column_id, "name": "Kolona 1", "width": 400.0, "shelves": 2}
        st.session_state.columns_data = [first]
        st.rerun()

# A column's shelf spacing is stored in widget state under a stable ID. Inputs are
# clear gaps: bottom-to-first shelf, shelf-to-shelf gaps, and last shelf-to-top.
for idx, col in enumerate(list(st.session_state.columns_data)):
    cid = col["id"]
    with st.container(border=True):
        title_col, remove_col = st.columns([4, 1])
        with title_col:
            st.markdown(f"### {col['name']}")
        with remove_col:
            if st.button("🗑️ Ukloni", key=f"remove_{cid}", disabled=len(st.session_state.columns_data) <= 1, use_container_width=True):
                st.session_state.columns_data = [c for c in st.session_state.columns_data if c["id"] != cid]
                st.rerun()
        a, b = st.columns(2)
        with a:
            new_name = st.text_input("Naziv kolone", value=col["name"], key=f"name_{cid}")
            new_width = st.number_input(f"Čista unutrašnja širina ({unit})", min_value=1.0, value=float(col["width"]), step=10.0, key=f"width_{cid}")
        with b:
            new_shelves = st.number_input("Broj polica u ovoj koloni", min_value=0, max_value=30, value=int(col["shelves"]), step=1, key=f"shelves_{cid}")
            st.caption("Za 0 polica nema unosa razmaka.")
        col["name"] = new_name.strip() or f"Kolona {cid}"
        col["width"] = float(new_width)
        old_shelves = int(col["shelves"])
        col["shelves"] = int(new_shelves)
        if col["shelves"] != old_shelves:
            st.rerun()

        if col["shelves"] > 0:
            st.markdown("**Slobodni razmaci po visini**")
            st.caption("Unesi razmake između površina polica, ne udaljenost od sredine jedne police do druge. Razmak dna i vrha podešavaš zasebno.")
            gap_keys = [f"gap_{cid}_{j}" for j in range(col["shelves"] + 1)]
            # Defaults are only initial suggestions; user can edit every gap independently.
            default_gap = max(0.0, (height - 2 * thickness - col["shelves"] * thickness) / (col["shelves"] + 1))
            for j in range(col["shelves"] + 1):
                if gap_keys[j] not in st.session_state:
                    st.session_state[gap_keys[j]] = round(default_gap, 1)
            gap_values = []
            for start in range(0, len(gap_keys), 2):
                pair = st.columns(2)
                for off in range(2):
                    j = start + off
                    if j >= len(gap_keys):
                        continue
                    if j == 0:
                        label = f"Dno do police 1 ({unit})"
                    elif j == col["shelves"]:
                        label = f"Police {col['shelves']} do vrha ({unit})"
                    else:
                        label = f"Polica {j} do police {j+1} ({unit})"
                    with pair[off]:
                        gap_values.append((j, st.number_input(label, min_value=0.0, value=float(st.session_state[gap_keys[j]]), step=10.0 if unit == "mm" else 1.0, key=gap_keys[j])))
            col["gaps"] = [float(st.session_state[k]) for k in gap_keys]
        else:
            col["gaps"] = []

# Store updates are in session state so add/remove actions preserve the current layout.
st.session_state.columns_data = cols

# Calculations: outer side panels + top/bottom + one vertical divider between adjacent columns.
inner_height = height - 2 * thickness
inner_depth = depth - thickness
outer_width_from_columns = 2 * thickness + sum(float(c["width"]) for c in cols) + max(0, len(cols) - 1) * thickness
issues = []
if thickness * 2 >= width:
    issues.append("Dvije bočne ploče su jednake ili šire od ukupne širine.")
if thickness * 2 >= height:
    issues.append("Gornja i donja ploča su jednake ili deblje od ukupne visine.")
if thickness >= depth:
    issues.append("Debljina ploče je jednaka ili veća od dubine.")
if any(float(c["width"]) <= 0 for c in cols):
    issues.append("Sve širine kolona moraju biti veće od nule.")
if abs(outer_width_from_columns - width) > 0.001:
    difference = outer_width_from_columns - width
    if difference > 0:
        issues.append(f"Kolone zahtijevaju ukupnu širinu {outer_width_from_columns:.1f} {unit}, što je {difference:.1f} {unit} više od zadane vanjske širine {width:.1f} {unit}.")
    else:
        issues.append(f"Unesene kolone zauzimaju širinu {outer_width_from_columns:.1f} {unit}; ostaje {abs(difference):.1f} {unit} neobjašnjene širine u odnosu na vanjsku širinu {width:.1f} {unit}.")
if inner_height <= 0 or inner_depth <= 0:
    issues.append("Visina ili dubina unutrašnjeg prostora nije pozitivna; provjeri dimenzije.")

cut_rows = [
    {"Dio": "Bočna stranica", "Količina": 2, f"Širina ({unit})": height, f"Dubina ({unit})": depth},
    {"Dio": "Gornja ploča", "Količina": 1, f"Širina ({unit})": max(0.0, width - 2 * thickness), f"Dubina ({unit})": depth},
    {"Dio": "Donja ploča", "Količina": 1, f"Širina ({unit})": max(0.0, width - 2 * thickness), f"Dubina ({unit})": depth},
]
if len(cols) > 1:
    cut_rows.append({"Dio": "Unutrašnja vertikalna pregrada", "Količina": len(cols)-1, f"Širina ({unit})": inner_height, f"Dubina ({unit})": depth})

for col in cols:
    n = int(col["shelves"])
    if n > 0:
        cut_rows.append({"Dio": f"Polica — {col['name']}", "Količina": n, f"Širina ({unit})": float(col["width"]), f"Dubina ({unit})": inner_depth})
        gaps = col.get("gaps", [])
        total_clear = sum(gaps)
        required = total_clear + n * thickness
        if inner_height > 0 and required > inner_height + 0.001:
            issues.append(f"{col['name']}: police i uneseni razmaci zauzimaju {required:.1f} {unit}, a unutrašnja visina je {inner_height:.1f} {unit}.")
        elif inner_height > 0:
            remaining = inner_height - required
            # gaps include bottom, between each shelf, and top; report unallocated space if any.
            if remaining > 0.001:
                issues.append(f"{col['name']}: ostalo je {remaining:.1f} {unit} neiskorištene visine. Povećaj neki razmak ako želiš da raspored pokrije cijelu visinu.")

st.divider()
st.subheader("4. Provjera i lista za rezanje")
summary, validation = st.columns([1, 1])
with summary:
    st.metric("Broj kolona", len(cols))
    st.metric("Unutrašnja visina", f"{inner_height:.1f} {unit}" if inner_height > 0 else "Provjeri dimenzije")
    st.metric("Širina potrebna za unesene kolone", f"{outer_width_from_columns:.1f} {unit}")
with validation:
    if issues:
        st.warning("Potrebno je provjeriti sljedeće stavke:")
        for issue in issues:
            st.write(f"• {issue}")
    else:
        st.success("Osnovne dimenzije i uneseni razmaci prolaze osnovne matematičke provjere.")
        st.caption("Ovo nije potpuna provjera konstrukcije, stabilnosti ili načina spajanja.")

cut_df = pd.DataFrame(cut_rows)
st.dataframe(cut_df, use_container_width=True, hide_index=True)
csv_data = cut_df.to_csv(index=False).encode("utf-8-sig")
st.download_button("Preuzmi listu za rezanje (CSV)", data=csv_data, file_name="lista_za_rezanje.csv", mime="text/csv")

st.caption("Napomena: ovo je preliminarna lista. Trenutna verzija pretpostavlja jednostavnu kutijastu konstrukciju, bočne stranice pune visine i unutrašnje pregrade pune visine. Ne obračunava leđa, vrata, kantovanje, spojeve, zazore, noge, ladice ni optimizaciju rezanja. Provjeri nacrt i mjere prije izrade.")
