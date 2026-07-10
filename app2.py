import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import plotly.express as px
from supabase import create_client

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="Laser Diode MES",
    layout="wide"
)

# -------------------------
# CUSTOM CSS
# -------------------------

st.markdown("""
<style>

.stApp{
    background: linear-gradient(
    135deg,
    #EEF4FF,
    #DDEAF7,
    #F8FAFC
    );
}

[data-testid="stSidebar"]{
    background:#0F172A;
}

[data-testid="stSidebar"] *{
    color:white;
}

h1,h2,h3{
    color:#003366;
    font-weight:bold;
}

[data-testid="stMetricValue"]{
    font-size:30px;
    font-weight:bold;
}

.stDataFrame{
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>

div.stButton > button{

background:#2563eb;
color:white;
border-radius:10px;
border:none;

}

div.stButton > button:hover{

background:#1d4ed8;
color:white;

}

</style>
""",unsafe_allow_html=True)


# -------------------------
# LOGIN
# -------------------------
# -----------------------------
# LOGIN PAGE
# -----------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.markdown("""
    <style>

    .loginbox{

    max-width:600px;
    margin:auto;
    margin-top:80px;

    padding:45px;

    border-radius:25px;

    background:
    linear-gradient(
    135deg,
    #020617,
    #1E3A8A,
    #0369A1
    );

    text-align:center;

    box-shadow:
    0px 15px 50px rgba(0,0,0,0.5);

    }


    .loginbox h1{

    color:white;

    font-size:48px;

    font-weight:900;

    letter-spacing:2px;

    }


    .loginbox h3{

    color:#BAE6FD;

    font-size:25px;

    }


    .loginbox p{

    color:white;

    font-size:20px;

    }


    </style>
    """,unsafe_allow_html=True)



    st.markdown("""
    <div class="loginbox">

    <h1>
    🔬 LASER DIODE MES
    </h1>

    <h3>
    Manufacturing Execution System
    </h3>

    <p>
    AI Based Fabrication Monitoring & Inspection
    </p>

    <p>
    🔐 Please Login
    </p>


    </div>

    """,unsafe_allow_html=True)
    name = st.text_input("👤 Full Name")

    email = st.text_input("📧 Email Address")
    role = st.selectbox(
    "Select Role",
    [
        "Scientist",
        "Technical Officer",
        "Technician",
        "Operator"
    ]
)

    if st.button("Login"):

        if name != "" and email != "":

            response = supabase.table("users") \
                 .select("*") \
                 .eq("email", email) \
                 .execute()
            
            if len(response.data) == 0:

                  supabase.table("users").insert({

                      "name": name,
                      "email": email,
                      "role": role,
                      "login_time": datetime.now().isoformat()

                   }).execute()
                
            st.session_state.logged_in = True
            st.session_state.user = name
            st.session_state.email = email
            st.session_state.role = role

            st.rerun()

        else:
            st.error("Please enter Name and Email.")

    st.stop()
# -------------------------
def generate_pdf(selected_wafer=None):

    pdf = FPDF()

    pdf.add_page()


    # -------------------------
    # HEADER
    # -------------------------

    pdf.set_fill_color(15,23,42)

    pdf.rect(
        0,
        0,
        210,
        30,
        "F"
    )


    pdf.set_text_color(
        255,
        255,
        255
    )

    pdf.set_font(
        "Arial",
        "B",
        18
    )


    pdf.cell(
        190,
        15,
        "LASER DIODE FABRICATION REPORT",
        align="C"
    )


    pdf.ln(20)


    # -------------------------
    # BASIC INFO
    # -------------------------

    pdf.set_text_color(
        0,
        0,
        0
    )

    pdf.set_font(
        "Arial",
        "",
        12
    )


    pdf.cell(
        190,
        10,
        f"Generated Date: {datetime.now()}",
        ln=True
    )


    pdf.cell(
        190,
        10,
        "Manufacturing Execution System",
        ln=True
    )


    pdf.ln(10)



    # -------------------------
    # WAFER DATA
    # -------------------------

    pdf.set_font(
        "Arial",
        "B",
        14
    )


    pdf.cell(
        190,
        10,
        "Wafer Registration Details",
        ln=True
    )


    pdf.set_font(
        "Arial",
        "",
        10
    )


    if selected_wafer:
        
        response = (
            supabase.table("wafers")
            .select("*")
            .eq("wafer_id", selected_wafer)
            .execute()
        )
        
    else:
        response = (
            supabase.table("wafers")
            .select("*")
            .execute()
        )
        
    wafer_data = pd.DataFrame(response.data)

    for index,row in wafer_data.iterrows():

        pdf.cell(
            190,
            8,
            f"Wafer ID: {row['wafer_id']} | Material: {row['material']} | Batch: {row['batch_no']}",
            ln=True
        )



    pdf.ln(10)



    # -------------------------
    # PROCESS DATA
    # -------------------------

    pdf.set_font(
        "Arial",
        "B",
        14
    )


    pdf.cell(
        190,
        10,
        "Fabrication Process History",
        ln=True
    )


    pdf.set_font(
        "Arial",
        "",
        9
    )


    if selected_wafer:
        
        response = (
            supabase.table("process_runs")
            .select("*")
            .eq("wafer_id", selected_wafer)
            .execute()
        )
        
    else:
        response = (
            supabase.table("process_runs")
            .select("*")
            .execute()
        )
        
    process_data = pd.DataFrame(response.data)

    for index,row in process_data.iterrows():

        pdf.multi_cell(
            190,
            7,
            f"""
Process: {row['process_name']}
Wafer: {row['wafer_id']}
Operator: {row['operator_name']}
Parameters: {row['parameters']}
Remarks: {row['remarks']}
Time: {row['timestamp']}

-----------------------------
"""
        )



    filename = "Laser_Diode_Fabrication_Report.pdf"


    pdf.output(
        filename
    )


    return filename
    
# -------------------------
# SIDEBAR
# -------------------------
# SIDEBAR USER AREA

st.sidebar.markdown("---")

st.sidebar.write("👤 User")

st.sidebar.write(
    st.session_state.get("user","Guest")
)

st.sidebar.write(
    "Role:",
    st.session_state.get("role","")
)


if st.sidebar.button("🚪 Logout"):

    st.session_state.logged_in=False
    st.session_state.user=""

    st.rerun()

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Wafer Registration",
        "Process Run Sheet",
        "View Data",
        "Reports",
        "Delete Records" 
    ]
)
process_flow = [
    "Wafer No + Breakdown Measurement",
    "Wafer Cleaning",
    "PLG Level I for Groove Etching",
    "Groove Etching",
    "PLG Level II for Mesa Etching",
    "Mesa Etching",
    "SiO2 Deposition in PECVD",
    "PLG Level II for SiO2 Etching",
    "SiO2 Etching",
    "PLG Level III for Metal Lift-off",
    "Metallization",
    "Metal Lift-off",
    "Annealing",
    "Cleaving",
    "Facet Coating",
    "Wire Bonding",
    "Testing"
]

if "current_step" not in st.session_state:
    st.session_state.current_step = 0


if "run_saved" not in st.session_state:
    st.session_state.run_saved = False

if "fabrication_completed" not in st.session_state:
    st.session_state.fabrication_completed = False

if "show_inspection" not in st.session_state:
    st.session_state.show_inspection = False

orientation = ""
edges = ""
visual = ""
etch_depth_edge = ""
mesa_height = ""
roughness = ""
breakdown = ""
breakdown_open_area = ""
dicd = ""
final_inspection = ""
    

# -------------------------
# DASHBOARD
# -------------------------
if page == "Dashboard":

    st.markdown(f"""

    <div style="
    background:linear-gradient(90deg,#001F54,#034078,#1282A2);
    padding:30px;
    border-radius:20px;
    color:white;
    text-align:center;
    ">

    <h1>
    👋 Welcome {st.session_state.get("user","Operator")}
    </h1>

    <h2>
    🔬 Laser Diode Manufacturing Execution System
    </h2>

    <p>
    Fabrication Monitoring Dashboard
    </p>

    </div>

    """,unsafe_allow_html=True)
    wafer_count = len(
         supabase.table("wafers")
         .select("wafer_id")
         .execute()
         .data
    )

    process_count = len(
          supabase.table("process_runs")
          .select("id")
          .execute()
          .data
    )
    
    process_data = (
          supabase.table("process_runs")
          .select("operator_name")
          .execute()
          .data
    )

    operator_count = len(
           set(
                row["operator_name"]
                for row in process_data
                if row["operator_name"]
           )
    )

    

    col1,col2,col3,col4 = st.columns(4)

    cards = [
    ("🧪 Wafers", wafer_count, "#2563EB"),
    ("⚙ Processes", process_count, "#059669"),
    ("👨‍🔬 Operators", operator_count, "#7C3AED"),   
    ("📈 Yield", "92%" if process_count > 0 else "0%", "#DC2626")
    ]

    for col,(title,val,color) in zip([col1,col2,col3,col4],cards):
         with col:
             st.markdown(f"""
             <div style="
             background:{color};
             padding:20px;
             border-radius:15px;
             text-align:center;
             color:white;">
             <h4>{title}</h4>
             <h1>{val}</h1>
             </div>
             """, unsafe_allow_html=True)
    st.info(
        f"Current Manufacturing Step: {process_flow[st.session_state.current_step]}"
    )
    st.subheader("🏭 Fabrication Workflow")

    workflow_display = []

    for i, step in enumerate(process_flow):

        if i < st.session_state.current_step:
            workflow_display.append(
                f"{step} ✅"
            )

        elif i == st.session_state.current_step:
            workflow_display.append(
                f"{step} 🔄"
            )

        else:
            workflow_display.append(
                f"{step} ⏳"
            )


    st.write(
        " → ".join(workflow_display)
    )


    progress = (
        st.session_state.current_step
        /
        (len(process_flow)-1)
    )

    st.progress(progress)
    
    processes = (
          supabase.table("process_runs")
          .select("process_name")
          .execute()
          .data
    )
    
    chart_data = (
         pd.DataFrame(processes)
         .groupby("process_name")
         .size()
         .reset_index(name="Count")
    )

    if len(chart_data)>0:
         fig = px.pie(
             chart_data,
             values="Count",
             names="process_name",
             title="Fabrication Process Distribution"
         )
         st.plotly_chart(fig, width="stretch")

    st.subheader("🔍 Wafer Search")

    search = st.text_input("Enter Wafer ID")

    if search:
         result = (
             supabase.table("process_runs")
             .select("*")
             .eq("wafer_id", search)
             .execute()
         )
        
         st.dataframe(pd.DataFrame(result.data))
        

    st.subheader("🖥 Equipment Status")

    equipment = [
        ("Mask Aligner", "ONLINE"),
        ("Evaporator", "ONLINE"),
        ("Annealing Furnace", "MAINTENANCE")
    ]


    col1,col2,col3 = st.columns(3)

    for col,(name,status) in zip(
        [col1,col2,col3],
        equipment
    ):

        with col:

            if status=="ONLINE":
                st.success(
                    f"{name}: {status}"
                )

            else:
                st.warning(
                    f"{name}: {status}"
                )
    st.subheader("📋 Recent Fabrication Activity")
    
    recent = (
        supabase.table("process_runs")
        .select("*")
        .order("id", desc=True)
        .limit(10)
        .execute()
    )
    
    st.dataframe(
        pd.DataFrame(recent.data),
        width="stretch"
    )

   

# -------------------------
# WAFER REGISTRATION
# -------------------------
elif page == "Wafer Registration":

    st.header("Wafer Registration")

    wafer_id = st.text_input(
        "Wafer ID"
    )

    material = st.selectbox(
        "Material",
        ["GaAs","InP","GaN"]
    )

    diameter = st.number_input(
        "Diameter (inch)"
    )

    batch_no = st.text_input(
        "Batch Number"
    )

    if st.button(
        "Register Wafer"
    ):

        try:
            data = {
                "wafer_id": wafer_id,
                "material": material,
                "diameter": diameter,
                "status": "Registered",
                "batch_no": batch_no,
                "created_at": datetime.now().isoformat()
            }
            
            supabase.table("wafers").insert(data).execute()
            st.success("Wafer Registered Successfully!")
            
        except Exception as e:
            if "duplicate key" in str(e).lower():
                st.warning("⚠️ Wafer already registered!")
            else:
                st.error(str(e))
        

# -------------------------
# PROCESS RUN SHEET
# -------------------------

elif page == "Process Run Sheet":

    st.header("Process Run Sheet")

    if "current_step" not in st.session_state:
        st.session_state.current_step = 0


    if "process_box" not in st.session_state:
         st.session_state.process_box = process_flow[0]

    process = st.selectbox(
       "Current Process",
       process_flow,
       index=st.session_state.current_step
    )
      
 
    progress = (
        (st.session_state.current_step)
        /
        (len(process_flow)-1)
    )

    st.progress(progress)

    st.info(
        f"Step {st.session_state.current_step+1} / {len(process_flow)} : {process}"
    ) 
    
    response = supabase.table("wafers").select("wafer_id").execute()
    
    wafers = pd.DataFrame(response.data)

    if len(wafers)==0:

        st.warning(
            "Register Wafer First"
        )

    else:

        st.subheader("🧪 Wafer Selection")

        mass_mode = st.checkbox(
              "Enable Mass Wafer Processing"
        )


        if mass_mode:

              selected_wafers = st.multiselect(
                  "Select Multiple Wafers",
                  wafers["wafer_id"]
              )

        else:

              selected_wafers = [
                  st.selectbox(
                     "Select Wafer",
                     wafers["wafer_id"],
                     key="single_wafer"
                  )
              ]

        operator = st.text_input(
            "Operator Name"
        )

        params = ""
        
        # Wafer No + Breakdown Measurement
        if process=="Wafer No + Breakdown Measurement":

            wafer_no = st.text_input("Wafer Number")

            breakdown = st.number_input(
                "Breakdown Voltage Measurement"
            )

            params = (
                f"Wafer={wafer_no}, "
                f"Breakdown={breakdown}V"
            )

        # Wafer Cleaning
        elif process=="Wafer Cleaning":

            acetone = st.number_input(
                "Acetone Spray Time (sec)"
            )

            ipa = st.number_input(
                "IPA Spray Time (sec)"
            )

            n2 = st.number_input(
                "N2 Purge Time (sec)"
            )

            final_clean = st.number_input(
                "Fresh Acetone Time (min)"
            )
          
            temp = st.number_input(
                "Fresh Acetone Temperature (°C)"
            )
            params= (
                f"Acetone={acetone}s,"
                f"IPA={ipa}s,"
                f"N2 Purge={n2}s,"
                f"Fresh Acetone={final_clean}min,"
                f"Temperature={temp}C"
            )

        # PLG Level I for Groove Etching
        elif process=="PLG Level I for Groove Etching":

            bake_temp = st.number_input(
                "Dehydration Bake Temperature"
            )

            bake_time = st.number_input(
                "Dehydration Bake Time (min)"
            )
            
            room_temp = st.number_input(
                 "Room Temperature (°C)"
            )


            humidity = st.number_input(
                "RH (%)"
            )

            pr = st.text_input(
                "PR Coat"
            )


            pr_thickness = st.number_input(
                "PR Thickness (µm)"
            )

            exposure_energy = st.number_input(
                "Exposure Energy (mJ)"
            )

            exposure_time = st.number_input(
                "Exposure Time"
            )
             
            peb_temp = st.number_input(
                "PEB Temperature (°C)"
            )


            peb_time = st.number_input(
                "PEB Time (sec)"
            )


            developer = st.text_input(
                "Developer Name"
            )


            develop_time = st.number_input(
                "Develop Time (sec)"
            )

            asher = st.text_input(
                "Asher Equipment"
            )

            ashing_power = st.number_input(
                "Ashing Power (W)"
            )

            ashing_time = st.number_input(
                "Ashing Time (min)"
            )

            ashing_thickness = st.number_input(
                "Ashing Thickness (Å)"
            )


            params= (
                f"Dehydration Bake={bake_temp}C/{bake_time}min,"
                f"Room Temp={room_temp}C,"
                f"RH={humidity}%,"
                f"PR={pr},"
                f"PR Thickness={pr_thickness}µm,"
                f"Exposure={exposure_energy}mJ,"
                f"Exposure Time={exposure_time},"
                f"PEB={peb_temp}C/{peb_time}s,"
                f"Developer={developer},"
                f"Develop={develop_time}s,"
                f"Asher={asher},"
                f"Ashing Power={ashing_power}W,"
                f"Ashing Time={ashing_time}min,"
                f"Ashing Thickness={ashing_thickness}A"
            )

        # Groove Etching
        elif process=="Groove Etching":

            hard_bake_temp = st.number_input(
                "Hard Bake Temperature (°C)"
            )


            hard_bake_time = st.number_input(
                "Hard Bake Time (min)"
            )


            etch_depth = st.number_input(
                "Etch Depth (µm)"
            )

            chemical = st.text_input(
                "Chemical"
            )


            ratio = st.text_input(
                "Chemical Ratio"
            )

            etch_rate = st.number_input(
                "Etch Rate (µm/min)"
            )

            etch_time = st.number_input(
                "Etch Time (min)"
            )

            rinse_cycles = st.number_input(
                "Dump Rinse Cycles"
            )


            rinse_time = st.number_input(
                "Rinse Time (sec)"
            )


            dry_time = st.number_input(
                "Dry Time (sec)"
            )


            params= (
                f"Hard Bake={hard_bake_temp}C/{hard_bake_time}min,"
                f"Etch Depth={etch_depth}µm,"
                f"Chemical={chemical},"
                f"Ratio={ratio},"
                f"Etch Rate={etch_rate}nm/min,"
                f"Etch Time={etch_time}min,"
                f"Rinse Cycles={rinse_cycles},"
                f"Rinse Time={rinse_time}s,"
                f"Dry Time={dry_time}s"
            )

        # PLG Level II for Mesa Etching
        elif process=="PLG Level II for Mesa Etching":
         
            dehydration_temp = st.number_input(
                "Dehydration Bake Temperature (°C)"
            )

            dehydration_time = st.number_input(
                "Dehydration Bake Time (min)"
            )

            room_temp = st.number_input(
                "Room Temperature (°C)"
            )

            humidity = st.number_input(
                "RH (%)"
            )

            pr = st.text_input(
                "PR Coat"
            )

            pr_thickness = st.number_input(
                "PR Thickness (µm)"
            )

            exposure_energy = st.number_input(
                "Exposure Energy (mJ)"
            )

            peb_temp = st.number_input(
                "PEB Temperature (°C)"
            )

            peb_time = st.number_input(
                "PEB Time (sec)"
            )

            developer = st.text_input(
                "Developer Name"
            )

            develop_time = st.number_input(
                "Develop Time (sec)"
            )            

            params= (
                f"Dehydration Bake={dehydration_temp}°C/{dehydration_time}min,"
                f"Room Temp={room_temp}°C,"
                f"RH={humidity}%,"
                f"PR={pr},"
                f"PR Thickness={pr_thickness}µm,"
                f"Exposure Energy={exposure_energy}mJ,"
                f"PEB={peb_temp}°C/{peb_time}s,"
                f"Developer={developer},"
                f"Develop={develop_time}s"
            )

        # Mesa Etching 
        elif process=="Mesa Etching":

            hard_bake_temp = st.number_input(
                "Hard Bake Temperature (°C)"
            )

            hard_bake_time = st.number_input(
                "Hard Bake Time (min)"
            )

            etch_depth = st.number_input(
                "Mesa Etch Depth (nm)"
            )

            chemical = st.text_input(
                "Chemical"
            )

            chemical_ratio = st.text_input(
                "Chemical Ratio"
            )

            etch_rate = st.number_input(
                "Etch Rate"
            )

            etch_rate = st.number_input(
                "Etch Rate (Å/min)"
            )


            etch_time = st.number_input(
                "Etch Time (min)"
            )


            rinse_cycles = st.number_input(
                "Dump Rinse Cycles"
            )


            rinse_time = st.number_input(
                "Rinse Time (sec)"
            )


            dry_time = st.number_input(
                "Dry Time (sec)"
            )
            params= (
                f"Hard Bake={hard_bake_temp}°C/{hard_bake_time}min,"
                f"Mesa Etch Depth={etch_depth}Å,"
                f"Chemical={chemical},"
                f"Rate={etch_rate},"
                f"Chemical Ratio={chemical_ratio},"
                f"Etch Rate={etch_rate}Å/min,"
                f"Etch Time={etch_time}min,"
                f"Dump Rinse Cycles={rinse_cycles},"
                f"Rinse={rinse_time}s,"
                f"Dry={dry_time}s"
            )

        # SiO2 Deposition in PECVD
        elif process=="SiO2 Deposition in PECVD":

            sio2_thickness = st.number_input(
                "SiO2 Thickness (Å)"
            )

            bake_temp = st.number_input(
                "Bake Temperature (°C)"
            )

            bake_time = st.number_input(
                "Bake Time (min)"
            )

            pecvd_temp = st.number_input(
                "PECVD Bottom Electrode Temperature (°C)"
            )

            params= (
                f"SiO2 Thickness={sio2_thickness}Å,"
                f"Bake={bake_temp}°C/{bake_time}min,"
                f"PECVD Bottom Electrode Temperature={pecvd_temp}°C"     
            )

        # PLG Level II for SiO2 Etching
        elif process=="PLG Level II for SiO2 Etching":

            dehydration_temp = st.number_input(
                "Dehydration Bake Temperature (°C)"
            )

            dehydration_time = st.number_input(
                "Dehydration Bake Time (min)"
            )

            hmds = st.number_input(
                "HMDS Time"
            )

            pr = st.text_input(
                "PR"
            )

            pr_thickness = st.number_input(
                "PR Thickness (µm)"
            )

            soft_bake = st.text_input(
                "Soft Bake"
            )

            exposure_energy = st.number_input(
                "Exposure Energy (mJ)"
            )
            
            peb_temp = st.number_input(
                "PEB Temperature (°C)"
            )

            peb_time = st.number_input(
                "PEB Time (sec)"
            )

            developer = st.text_input(
                "Developer Name"
            )

            develop_time = st.number_input(
                "Develop Time (sec)"
            )            

            params= (
                f"Dehydration Bake={dehydration_temp}°C/{dehydration_time}min,"
                f"HMDS={hmds}min,"
                f"PR={pr},"
                f"PR Thickness={pr_thickness}µm,"
                f"Soft Bake={soft_bake},"
                f"Exposure Energy={exposure_energy}mJ,"
                f"PEB={peb_temp}°C/{peb_time}s,"
                f"Developer={developer},"
                f"Develop={develop_time}s"
            )

        # SiO2 Etching
        elif process=="SiO2 Etching":

            hard_bake_temp = st.number_input(
                "Hard Bake Temperature (°C)"
            )

            hard_bake_time = st.number_input(
                "Hard Bake Time (min)"
            )

            bHF = st.number_input(
                "BHF Time (sec)"
            )

            dump_cycles = st.number_input(
                "Dump Rinse Cycles"
            )

            rinse_time = st.number_input(
                "Rinse Time (sec)"
            )

            dry_time = st.number_input(
                "Dry Time (sec)"
            )

            params= (
                f"Hard Bake={hard_bake_temp}°C/{hard_bake_time}min,"
                f"BHF={bHF}s,"
                f"Dump Rinse={dump_cycles},"
                f"Rinse={rinse_time}s,"
                f"Dry={dry_time}s"
            )

        # PLG Level III for Metal Lift-off
        elif process=="PLG Level III for Metal Lift-off":

            dehydration_temp = st.number_input(
                "Dehydration Bake Temperature (°C)"
            )

            dehydration_time = st.number_input(
                "Dehydration Bake Time (min)"
            )


            vacuum_prime = st.number_input(
                "Vacuum Prime Time"
            )

            room_temp = st.number_input(
                "Room Temperature (°C)"
            )

            humidity = st.number_input(
                "RH (%)"
            )

            pr = st.text_input(
                "PR Coat"
            )

            pr_thickness = st.number_input(
                "PR Thickness (µm)"
            )

            exposure_energy = st.number_input(
                "Exposure Energy (mJ)"
            )

            cb_treatment = st.number_input(
                "CB Treatment Time"
            )

            peb_temp = st.number_input(
                "PEB Temperature (°C)"
            )

            peb_time = st.number_input(
                "PEB Time (sec)"
            )

            developer = st.text_input(
                "Developer Name"
            )

            develop_time = st.number_input(
                "Develop Time (sec)"
            )            
            
            asher = st.text_input(
                "Asher Equipment"
            )

            ashing_power = st.number_input(
                "Ashing Power (W)"
            )

            ashing_time = st.number_input(
                "Ashing Time (min)"
            )
            
            ashing_thickness = st.number_input(
                "Ashing Thickness (Å)"
            )
            
            rinse_time = st.number_input(
                "Rinse Time (sec)"
            )

            dry_time = st.number_input(
                "Dry Time (sec)"
            )

            
            params= (
                f"Dehydration Bake={dehydration_temp}C/{dehydration_time}min,"
                f"Vacuum Prime={vacuum_prime}min,"
                f"Room Temp={room_temp}C,"
                f"RH={humidity}%,"
                f"PR={pr},"
                f"PR Thickness={pr_thickness}µm,"
                f"Exposure={exposure_energy}mJ,"
                f"CB Treatment={cb_treatment}min,"
                f"PEB={peb_temp}C/{peb_time}s,"
                f"Developer={developer},"
                f"Develop={develop_time}s,"
                f"Asher={asher},"
                f"Ashing Power={ashing_power}W,"
                f"Ashing Time={ashing_time}min,"
                f"Ashing Thickness={ashing_thickness}A,"
                f"Rinse={rinse_time}s,"
                f"Dry={dry_time}s"
            )

        # Metallization
        elif process=="Metallization":

            pretreatment = st.text_input(
                "Pre Metal Treatment"
            )
 
            rinse_cycles = st.number_input(
                "Dump Rinse Cycles"
            )

            rinse_time = st.text_input(
                "Rinse Time"
            )

            dry_time = st.text_input(
                "Dry Time"
            )

            metal_scheme = st.text_input(
                "Metal Scheme"
            )

            thickness = st.number_input(
                "Metal Thickness (A)"
            )

            params= (
                f"Treatment={pretreatment},"
                f"Dump Rinse Cycles={rinse_cycles},"
                f"Rinse Time={rinse_time},"
                f"Dry Time={dry_time},"
                f"Metal Scheme={metal_scheme},"
                f"Thickness={thickness}A"
            )

        # Metal Lift-off
        elif process=="Metal Lift-off":

            lift_pressure = st.number_input(
                "Lift-off Pressure"
            )

            clean = st.number_input(
                "Final Clean Time"
            )

            rinse_cycles = st.number_input(
                "Dump Rinse Cycles"
            )

            rinse_time = st.text_input(
                "Rinse Time"
            )

            dry_time = st.text_input(
                "Dry Time"
            )

            params= (
                f"Pressure={lift_pressure},"
                f"Final Clean={clean}min,"
                f"Dump Rinse Cycles={rinse_cycles},"
                f"Rinse Time={rinse_time},"
                f"Dry Time={dry_time}"
            )


        # ANNEALING
        elif process=="Annealing":

            temp = st.number_input(
                "Temperature (°C)"
            )

            duration = st.number_input(
                "Duration (min)"
            )

            if temp > 450:
                st.warning(
                    "Temperature above SOP"
                )

            params = f"Temp={temp}, Duration={duration}"
        
        # CLEAVING

        elif process=="Cleaving":

            cleave_angle = st.number_input(
                "Cleaving Angle (degree)"
            )

            edge_quality = st.selectbox(
                "Edge Quality",
                [
                    "Good",
                    "Average",
                    "Poor"
                ]
            )

            params = (
                f"Angle={cleave_angle}, "
                f"Edge Quality={edge_quality}"
            )



        # FACET COATING

        elif process=="Facet Coating":

            coating = st.text_input(
                "Coating Material"
            )

            thickness = st.number_input(
                "Coating Thickness (nm)"
            )

            uniformity = st.selectbox(
                "Coating Uniformity",
                [
                    "Pass",
                    "Fail"
                ]
            )

            params = (
                f"Material={coating}, "
                f"Thickness={thickness}, "
                f"Uniformity={uniformity}"
            )



        # WIRE BONDING

        elif process=="Wire Bonding":

            wire_material = st.text_input(
                "Wire Material"
            )

            bond_temp = st.number_input(
                "Bond Temperature (°C)"
            )

            pull_strength = st.number_input(
                "Pull Strength (g)"
            )

            params = (
                f"Wire={wire_material}, "
                f"Temperature={bond_temp}, "
                f"Strength={pull_strength}"
            )




        # TESTING
        elif process=="Testing":

            current = st.number_input(
                "Threshold Current (mA)"
            )

            power = st.number_input(
                "Output Power (mW)"
            )

            wavelength = st.number_input(
                "Wavelength (nm)"
            )

            params = f"Current={current}, Power={power}, Wavelength={wavelength}"

        remarks = st.text_area(
            "Remarks"
        )

        if st.button("🔍 Inspect", key="inspect_button"):
           st.session_state.show_inspection = True
            
        if st.session_state.show_inspection:
           inspection_data = {}

           if process=="Cleaning":
               inspection_data={
                  "acetone":acetone,
                  "ipa":ipa
               }

           elif process=="PLG Level I for Groove Etching":
               inspection_data={
                  "orientation": orientation,
                  "edges": edges,
                  "visual_check": visual
               }

           elif process=="Groove Etching":
               inspection_data={
                  "etch_depth": etch_depth
               }

           elif process=="PLG Level II for Mesa Etching":
               inspection_data={
                  "orientation": orientation,
                  "edges": edges,
                  "visual_check": visual
               }

           elif process=="Mesa Etching":
               inspection_data={
                  "etch_depth_edge": etch_depth_edge,
                  "mesa_height": mesa_height,
                  "roughness_measurement": roughness
               }


           elif process=="SiO2 Deposition in PECVD":
               inspection_data={
                  "sio2_thickness": sio2_thickness
               }


           elif process=="PLG Level II for SiO2 Etching":
               inspection_data={
                  "breakdown_measurement": breakdown
               }


           elif process=="SiO2 Etching":
               inspection_data={
                  "breakdown_open_area": breakdown_open_area
               }


           elif process=="PLG Level III for Metal Lift-off":
               inspection_data={
                  "DICD": dicd
               }


           elif process=="Metallization":
               inspection_data={
                  "metal_scheme": metal_scheme,
                  "thickness": thickness
               }


           elif process=="Metal Lift-off":
               inspection_data={
                  "final_inspection": final_inspection
               }
           
           elif process=="Annealing":
               inspection_data={
                  "temp":temp,
                  "duration":duration
               }

           elif process=="Cleaving":
               inspection_data={
                  "angle":cleave_angle
           }


           elif process=="Facet Coating":
               inspection_data={
                  "thickness":thickness
           }


           elif process=="Wire Bonding":
               inspection_data={
                  "strength":pull_strength
           }

           elif process=="Testing":
              inspection_data={
                  "current":current,
                  "power":power,
                  "wavelength":wavelength
               }
           
           st.subheader("🔍 Process Inspection Points")

           inspection_database = {

           "Wafer No + Breakdown Measurement":
           [
           "Wafer identification check",
           "Breakdown voltage verification"
           ],

           "Wafer Cleaning":
           [
           "Surface contamination check",
           "PR cleaning verification",
           "Particle removal check"
           ],

           "PLG Level I for Groove Etching":
           [
           "PR thickness verification",
           "Exposure quality check",
           "Pattern alignment check",
           "Developer inspection",
           "Ashing process verification"
           ],

           "Groove Etching":
           [
           "Etch depth verification",
           "Etch rate check",
           "Sidewall profile inspection",
           "Rinse and dry quality check"
           ],

           "PLG Level II for Mesa Etching":
           [
           "PR thickness verification",
           "Pattern alignment check",
           "Exposure quality check",
           "Orientation verification",
           "Edge inspection"
           ],

           "Mesa Etching":
           [
           "Mesa height measurement",
           "Etch depth verification",
           "Surface damage inspection",
           "Roughness measurement"
           ],

           "SiO2 Deposition in PECVD":
           [
           "Pre-Inspection",
           "Breakdown measurement",
           "Surface condition check",
           "SiO2 thickness verification",
           "Film uniformity inspection",
           "PECVD deposition quality check"
           ],
 
           "PLG Level II for SiO2 Etching":
           [
           "Pattern alignment check",
           "Edge inspection",
           "PR profile verification"
           ],

           "SiO2 Etching":
           [
           "Breakdown measurement on open area",
           "PR Clean verification",
           "Final clean verification",
           "Surface cleanliness check",
           "Rinse and dry quality check"
           ],

           "PLG Level III for Metal Lift-off":
           [
           "Inspect after develop",
           "DICD inspection"
           ],

           "Metallization":
           [
           "Metal thickness verification",
           "Layer uniformity"
           ],

           "Metal Lift-off":
           [
           "Pattern removal check",
           "Final surface inspection"
           ],

           "Annealing":
           [
           "Temperature profile check",
           "Material activation",
           "Surface condition"
           ],

           "Cleaving":
           [
           "Cleave angle verification",
           "Facet quality inspection",
           "Edge damage inspection"
           ],

           "Facet Coating":
           [
           "Coating thickness verification",
           "Facet reflectivity check",
           "Uniform coating inspection"
           ],


           "Wire Bonding":
           [
           "Bond strength verification",
           "Wire alignment check",
           "Electrical connection inspection"
           ],

           "Testing":
           [
           "Current verification",
           "Optical power check",
           "Wavelength accuracy"
           ]
           
           }

           for i, point in enumerate(
               inspection_database.get(process, [])
           ):

               key = f"inspect_{process}_{i}"

               st.checkbox(
                  point,
                  key=key
               )
     
           st.subheader("📐 Geometry Consideration")


           geometry_database = {

           "Wafer No + Breakdown Measurement":
           "Wafer breakdown measurement verification",
           
           "Wafer Cleaning":
           "Wafer surface flatness and scratch inspection",

           "PLG Level I for Groove Etching":
           "Groove pattern geometry verification",

           "Groove Etching":
           "Etch depth measurement verification",

           "PLG Level II for Mesa Etching":
           "Mesa pattern geometry verification",

           "Mesa Etching":
           "Mesa height measurement and etch depth at edge verification",

           "SiO2 Deposition in PECVD":
           "SiO2 thickness verification",

           "PLG Level II for SiO2 Etching":
           "Pattern opening geometry verification",

           "SiO2 Etching":
           "Breakdown measurement on open area",

           "PLG Level III for Metal Lift-off":
           "Pattern geometry verification after lift-off",

           "Metallization":
           "Metal scheme and thickness verification",

           "Metal Lift-off":
           "Metal removal and final structure verification",

           "Annealing":
           "Surface morphology and thermal stability",
           
           "Cleaving":
           "Facet angle and chip dimension verification",

           "Facet Coating":
           "Facet surface and coating thickness verification",

           "Wire Bonding":
           "Bond position and wire geometry verification",

           "Testing":
           "Emission profile and device geometry"

           }


           geometry_key = "geometry_check_" + process



           st.checkbox(
               geometry_database.get(process,"Manual geometry verification"),
               key=geometry_key
           ) 

           
           if st.button("Inspect & Save Run Sheet", key="inspect_save"):
           
               for wafer_id in selected_wafers:
    
                   data = {
                       "wafer_id": wafer_id,
                       "process_name": process,
                       "operator_name": operator,
                       "parameters": params,
                       "remarks": remarks,
                       "timestamp": datetime.now().isoformat()
                   }
                   
                   supabase.table("process_runs").insert(data).execute()    
                   
               inspection_points = []
    
               for i, point in enumerate(inspection_database[process]):
    
                   if st.session_state.get(
                      f"inspect_{process}_{i}",
                      False
                   ):
                      inspection_points.append(point)
    
               geometry_checked = st.session_state.get(
                   "geometry_check_"+process,
                   False
               )
    
               inspection = {
                   "wafer_id": selected_wafers[0],
                   "process_name": process,
                   "inspection_point": str(inspection_points),
                   "geometry_check": str(geometry_checked),
                   "status": "Manual Inspection Completed",
                   "remarks": remarks,
                   "timestamp": datetime.now().isoformat()
               }
               
               supabase.table("inspections").insert(inspection).execute()
               
               
               st.success("Run Sheet Saved")
               st.session_state.run_saved = True

        if st.session_state.run_saved:

           if st.button(
            "➡️ Next Process",
            key="next_process"
           ):
          
             


               if st.session_state.current_step < len(process_flow)-1:

                  st.session_state.current_step += 1

                  st.session_state.run_saved = False
                  st.session_state.show_inspection = False
               
                  for key in list(st.session_state.keys()):

                      if key.startswith("inspect_") or key.startswith("geometry_check_"):
                          del st.session_state[key]

   
                 

                  st.rerun()

               else:

                  
                  st.success(
                      "🎉 Fabrication Flow Completed Successfully"
                  )
                  import time
                  time.sleep(2) 
                   
                  st.session_state.current_step = 0
                  st.session_state.run_saved = False
                  st.session_state.fabrication_completed = True 

                  for key in list(st.session_state.keys()):
                      if key.startswith("inspect_") or key.startswith("geometry_check_"):
                          del st.session_state[key]
                   
                  st.rerun()  
    
# -------------------------
# VIEW DATA
# -------------------------
elif page == "View Data":

    st.header("Registered Wafers")
    
    response = supabase.table("wafers").select("*").execute()
    wafer_df = pd.DataFrame(response.data)
    st.dataframe(wafer_df)

    st.header("Process History")
    
    response = supabase.table("process_runs").select("*").execute()
    process_df = pd.DataFrame(response.data)
    st.dataframe(process_df)
    
# -------------------------
# Reports
# -------------------------
elif page == "Reports":

    st.markdown("""
    <div style="
    background:linear-gradient(90deg,#001F54,#034078,#1282A2);
    padding:25px;
    border-radius:20px;
    color:white;
    text-align:center;">
    <h1>📄 Laser Diode Report Center</h1>
    <p>Generate fabrication reports for complete production history</p>
    </div>
    """, unsafe_allow_html=True)


    report_type = st.radio(
        "Select Report Type",
        [
            "All Wafers",
            "Specific Wafer"
        ]
    )


    selected_wafer = None


    if report_type == "Specific Wafer":

        response = (
            supabase.table("wafers")
            .select("wafer_id")
            .execute()
        )
        
        wafer_list = pd.DataFrame(response.data)


        if len(wafer_list)==0:

            st.warning(
                "No wafers available"
            )

        else:

            selected_wafer = st.selectbox(
                "Select Wafer ID",
                wafer_list["wafer_id"]
            )



    if st.button(
        "🚀 Generate PDF Report"
    ):


        file = generate_pdf(
            selected_wafer
        )


        with open(file,"rb") as f:

            st.download_button(
                "⬇ Download PDF",
                f,
                file_name=file,
                mime="application/pdf"
            )
# -------------------------
# Delete Records
# -------------------------

elif page=="Delete Records":

    if st.session_state.get("role") != "Scientist":
        st.error(
            "Only Scientist can access Delete Records"
        )
        st.stop()


    st.header("🗑 Delete MES Records")


    delete_type = st.selectbox(
        "Select Data",
        [
            "Delete Wafer",
            "Delete Process Record"
        ]
    )


    if delete_type=="Delete Wafer":

        response = (
            supabase.table("wafers")
            .select("wafer_id")
            .execute()
        )
        
        wafers = pd.DataFrame(response.data)


        if len(wafers)>0:

            wafer = st.selectbox(
                "Select Wafer",
                wafers["wafer_id"]
            )


            if st.button(
                "Delete Wafer"
            ):

                supabase.table("wafers") \
                    .delete() \
                    .eq("wafer_id", wafer) \
                    .execute()
                
                supabase.table("process_runs") \
                    .delete() \
                    .eq("wafer_id", wafer) \
                    .execute()

                


                st.success(
                    "Wafer deleted successfully"
                )



    else:

        response = (
            supabase.table("process_runs")
            .select("id,wafer_id,process_name")
            .execute()
        )
        
        records = pd.DataFrame(response.data)


        if len(records)>0:


            record_id=st.selectbox(
                "Select Process Record",
                records["id"]
            )


            if st.button(
                "Delete Process"
            ):


                supabase.table("process_runs") \
                    .delete() \
                    .eq("id", record_id) \
                    .execute()




                st.success(
                    "Process record deleted"
                )
