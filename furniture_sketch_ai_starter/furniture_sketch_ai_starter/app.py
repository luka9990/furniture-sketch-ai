import io
import math
import pandas as pd
import streamlit as st
from PIL import Image

st.set_page_config(page_title='Furniture Sketch AI #0.2', page_icon='📐', layout='wide')
st.title('📐 Furniture Sketch AI')
st.caption('Verzija #0.2 — različite konstrukcije namještaja, noge, vrata i kuhinjski elementi')
st.info('Preliminarni obračun za planiranje. Prije rezanja provjeri okove, spojeve, nosivost, stabilnost, zazore i mjere na licu mjesta.')

with st.sidebar:
    st.header('Projekat')
    project = st.text_input('Naziv projekta', 'Moj namještaj')
    kind = st.selectbox('Vrsta namještaja', ['Ormar', 'Polica / regal', 'Komoda', 'Kuhinjski element', 'Sto', 'Stolica'])
    unit = st.selectbox('Jedinica', ['mm', 'cm'])
    st.caption('Sve mjere unosi u istoj jedinici.')

scale = 1 if unit == 'mm' else 10

def inp(label, mm, minimum=0, step=10, key=None):
    return st.number_input(f'{label} ({unit})', min_value=float(minimum)/scale, value=float(mm)/scale, step=float(step)/scale, key=key) * scale

def num(label, default, minimum=0, maximum=50, key=None):
    return st.number_input(label, min_value=minimum, max_value=maximum, value=default, step=1, key=key)

rows = []
notes = []
def part(name, count, length, width, detail=''):
    if count <= 0:
        return
    if length <= 0 or width <= 0:
        notes.append(f'{name}: neispravna dimenzija; dio nije dodat.')
        return
    rows.append({'Dio':name, 'Količina':int(count), f'Dužina ({unit})':round(length/scale,2), f'Širina ({unit})':round(width/scale,2), 'Napomena':detail})

left, right = st.columns([1,1], gap='large')
with left:
    st.subheader('1. Skica (opcionalno)')
    file = st.file_uploader('Dodaj skicu', type=['png','jpg','jpeg','webp'])
    if file:
        try: st.image(Image.open(file), use_container_width=True)
        except Exception: st.warning('Slika se ne može otvoriti.')
with right:
    st.subheader('2. Vanjske dimenzije')
    default = {'Ormar':(1200,2000,600), 'Polica / regal':(900,1800,350), 'Komoda':(1000,850,450), 'Kuhinjski element':(600,720,560), 'Sto':(1200,750,650), 'Stolica':(450,900,480)}[kind]
    w = inp('Širina', default[0], 1, key=f'w_{kind}')
    h = inp('Ukupna visina', default[1], 1, key=f'h_{kind}')
    d = inp('Dubina', default[2], 1, key=f'd_{kind}')
    t = inp('Debljina ploče', 18, 1, 1, key=f't_{kind}')

st.divider()
st.subheader('3. Konstrukcija i dijelovi')

if kind in ['Ormar','Polica / regal','Komoda','Kuhinjski element']:
    kitchen = kind == 'Kuhinjski element'
    if kitchen:
        kitchen_type = st.radio('Tip kuhinjskog elementa', ['Donji element', 'Viseći (gornji) element', 'Visoki element'], horizontal=True)
        if kitchen_type == 'Donji element':
            st.caption('Unesena visina predstavlja korpus bez nogica i radne ploče. Noge i radna ploča su posebne opcije.')
        else:
            st.caption('Unesena visina predstavlja visinu korpusa.')
    else:
        kitchen_type = None
    back = st.checkbox('Dodaj leđa (ploča iza korpusa)', value=True)
    back_t = inp('Debljina leđa', 3, 1, 1) if back else 0
    back_mode = st.selectbox('Postavljanje leđa', ['Na zadnju stranu korpusa (spolja)', 'Unutar korpusa (pojednostavljeno)']) if back else None
    ncol = int(num('Broj vertikalnih odjeljaka', 1, 1, 12))
    shelves = []
    st.markdown('**Police po odjeljku**')
    for i in range(ncol):
        shelves.append(int(num(f'Broj polica — odjeljak {i+1}', 2 if kind in ['Ormar','Polica / regal'] else 1, 0, 25, key=f'shelves_{kind}_{i}')))
    inner_w = w - (ncol + 1)*t
    bay_w = inner_w/ncol
    inner_h = h-2*t
    effective_d = d - (back_t if back and back_mode == 'Unutar korpusa (pojednostavljeno)' else 0)
    if inner_w <= 0 or inner_h <= 0 or effective_d <= 0:
        notes.append('Debljina i broj pregrada ne staju u zadane vanjske dimenzije.')
    else:
        part('Bočna stranica', 2, h, d)
        part('Gornja ploča korpusa', 1, w-2*t, d)
        part('Donja ploča korpusa', 1, w-2*t, d)
        part('Vertikalna pregrada', ncol-1, inner_h, effective_d)
        for i, count in enumerate(shelves):
            part(f'Polica — odjeljak {i+1}', count, bay_w, effective_d, 'Dubina police i pričvršćenje provjeriti prema okovu')
        if back:
            if back_mode == 'Na zadnju stranu korpusa (spolja)': part('Leđa', 1, h, w, f'Debljina {back_t/scale:g} {unit}; dodaje dubinu spolja')
            else: part('Leđa', 1, inner_h, w-2*t, f'Debljina {back_t/scale:g} {unit}; unutrašnja montaža, detalj spoja provjeriti')
    st.caption(f'Približna čista širina svakog odjeljka: {max(0,bay_w)/scale:.1f} {unit} (jednake širine).')

    if kind == 'Komoda':
        drawer_count = int(num('Broj ladica (opcionalno)', 0, 0, 12))
        if drawer_count:
            st.warning('Ladice su trenutno samo evidentirane; dimenzije njihovih stranica i vodilica nisu automatski obračunate.')
            notes.append(f'{drawer_count} ladica: izmjeriti fronte, kutije, vodilice i zazore prema odabranom okovu.')

    if kitchen and kitchen_type == 'Donji element':
        leg_count = int(num('Broj podesivih kuhinjskih nogica', 4, 0, 12))
        leg_h = inp('Visina nogica', 100, 1)
        countertop = st.checkbox('Uključi radnu ploču', value=False)
        if countertop:
            top_t = inp('Debljina radne ploče', 38, 1)
            overhang_front = inp('Prednji prepust radne ploče', 30, 0)
            overhang_side = inp('Bočni prepust sa svake strane', 0, 0)
            part('Radna ploča', 1, w+2*overhang_side, d+overhang_front, f'Debljina {top_t/scale:g} {unit}')
        notes.append(f'Kuhinjske nogice: {leg_count} kom, visina {leg_h/scale:g} {unit} (kupovni okov, nije ploča za rezanje).')
        st.metric('Visina sa nogicama' + (' i pločom' if countertop else ''), f'{(h+leg_h+(top_t if countertop else 0))/scale:.1f} {unit}')
        if st.checkbox('Dodaj soklu (masku ispod)', value=True):
            part('Prednja sokla', 1, w, leg_h, 'Prilagoditi sistemu kopči i nogica')
    elif kitchen and kitchen_type == 'Viseći (gornji) element':
        notes.append('Viseći element: obavezno odabrati odgovarajuće nosače i provjeriti nosivost zida i pričvršćenja.')

    if kind != 'Polica / regal':
        st.markdown('### 🚪 Vrata i otvaranje')
        door_count = int(num('Broj krila vrata (0 = bez vrata)', 2 if kind == 'Ormar' else 1, 0, 8, key=f'doors_{kind}'))
        if door_count:
            door_style = st.selectbox('Vrsta vrata', ['Preklopna (preko prednje ivice korpusa)', 'Umetnuta (unutar otvora)'])
            opening = st.selectbox('Otvaranje', ['Bočno — šarke', 'Podizanje nagore (preklop)', 'Spuštanje nadole (preklop)'] if kitchen else ['Bočno — šarke'])
            gap = inp('Zazor između krila i na ivicama', 2, 0, 1)
            if door_style.startswith('Preklopna'):
                door_total_w = w - (door_count+1)*gap
                door_h = h-2*gap
            else:
                door_total_w = w-2*t-(door_count+1)*gap
                door_h = h-2*t-2*gap
            door_w = door_total_w/door_count
            part('Fronta / vrata', door_count, door_h, door_w, f'{door_style}; {opening}; debljina {t/scale:g} {unit}')
            if opening == 'Bočno — šarke':
                hinges = int(num('Okvirni broj šarki po krilu', 3 if h >= 1200 else 2, 2, 8))
                notes.append(f'Okvirno {door_count*hinges} šarki ukupno; odabir šarki, preklop, položaj rupa i smjer svakog krila potvrditi prema katalogu proizvođača.')
                directions = []
                for i in range(door_count):
                    directions.append(st.selectbox(f'Krilo {i+1} — strana šarki', ['Lijevo', 'Desno'], index=i%2, key=f'dir_{kind}_{i}'))
                notes.append('Smjerovi krila: ' + ', '.join(f'{i+1}: {v}' for i,v in enumerate(directions)) + '.')
            else:
                notes.append('Preklopna vrata: potreban odgovarajući podizni/spuštajući mehanizam; okov i sile nisu izračunati.')
            st.caption(f'Približna mjera jednog krila: {door_h/scale:.1f} × {max(0,door_w)/scale:.1f} {unit}. Nije uračunat stvarni preklop šarke.')

elif kind == 'Sto':
    st.markdown('### 🪑 Ploča i noge stola')
    top_t = inp('Debljina ploče stola', 25, 1, 1)
    leg_count = int(num('Broj nogu', 4, 1, 12))
    leg_shape = st.selectbox('Presjek nogu', ['Kvadratni / pravougaoni', 'Okrugli (kupovne noge)'])
    leg_a = inp('Širina noge / prečnik', 60, 1)
    leg_b = inp('Dubina noge', 60, 1) if leg_shape.startswith('Kvadratni') else leg_a
    leg_h = h-top_t
    part('Ploča stola', 1, w, d, f'Debljina {top_t/scale:g} {unit}')
    if leg_shape.startswith('Kvadratni'):
        part('Noga stola', leg_count, leg_h, leg_a, f'Presjek {leg_a/scale:g} × {leg_b/scale:g} {unit}; dužina noge {leg_h/scale:g} {unit}')
    else:
        notes.append(f'{leg_count} okruglih nogu, prečnik {leg_a/scale:g} {unit}, visina {leg_h/scale:g} {unit}; kupovni dio, nije ploča za rezanje.')
    if st.checkbox('Dodaj prednje i zadnje vezne letve (apron)', value=True):
        rail_h = inp('Visina vezne letve', 90, 1)
        part('Prednja/zadnja vezna letva', 2, w-2*leg_a, rail_h)
        part('Bočna vezna letva', 2, d-2*leg_b, rail_h)
        notes.append('Vezne letve: provjeriti položaj, debljinu, spojeve i prostor za noge.')
    notes.append('Sto: provjeriti stabilnost, nosivost, način pričvršćivanja nogu i prevrtanje.')

elif kind == 'Stolica':
    st.markdown('### 🪑 Sjedište, noge i naslon')
    seat_h = inp('Visina sjedišta od poda', 450, 1)
    seat_t = inp('Debljina sjedišta', 25, 1, 1)
    leg_a = inp('Širina noge', 40, 1)
    leg_b = inp('Dubina noge', 40, 1)
    back_t = inp('Debljina ploče naslona', 18, 1, 1)
    back_width = inp('Širina naslona', 400, 1)
    back_h = inp('Visina naslona iznad sjedišta', 400, 1)
    part('Sjedište', 1, w, d, f'Debljina {seat_t/scale:g} {unit}')
    part('Prednja noga', 2, seat_h-seat_t, leg_a, f'Presjek {leg_a/scale:g} × {leg_b/scale:g} {unit}')
    part('Zadnja noga / nosač naslona', 2, h-seat_t, leg_a, 'Pojednostavljeno: ravna noga; stvarni ugao i spojevi nisu obračunati')
    part('Naslon', 1, back_h, back_width, f'Debljina {back_t/scale:g} {unit}')
    if st.checkbox('Dodaj bočne vezne letve', value=True):
        rail_h = inp('Visina vezne letve stolice', 60, 1)
        part('Bočna vezna letva', 2, d-2*leg_b, rail_h)
        part('Prednja/zadnja vezna letva', 2, w-2*leg_a, rail_h)
    if abs((seat_h+back_h)-h) > 1:
        notes.append('Visina sjedišta + visina naslona razlikuje se od ukupne visine; provjeri zadane dimenzije.')
    notes.append('Stolica: ovo je samo grubi popis pravih elemenata, ne konstrukcijski nacrt. Ugao naslona, zadnje noge, opterećenje i sigurnost moraju se posebno projektovati.')

st.divider()
st.subheader('4. Lista dijelova i napomene')
if rows:
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button('📥 Preuzmi listu za rezanje (CSV)', df.to_csv(index=False).encode('utf-8-sig'), file_name='lista_za_rezanje.csv', mime='text/csv')
else:
    st.error('Nema valjanih dijelova. Provjeri dimenzije.')
if notes:
    st.markdown('**Važne napomene:**')
    for note in notes: st.write('• '+note)
st.caption('Dimenzije dijelova su preliminarne. Nisu automatski izračunati rupe za šarke, kantovanje, šrafovi, tipli, klizači, mehanizmi, spojevi niti optimizacija ploča. Za proizvodnju koristi provjeren radionički nacrt.')
