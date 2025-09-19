import pandas as pd
import streamlit as st
import pymysql
import matplotlib.pyplot as plt
import cryptography

#DB connection

def new_connection():
    try:
        mydb = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="policedb"
        )
        return mydb
    except pymysql.MySQLError as e:
        st.error(f"Connection Error: {e}")
        return None
       
#fetch data

def fetch_data(query):
    conn=new_connection()
    if conn:
        try:
            cursor=conn.cursor()
            cursor.execute(query)
            data=cursor.fetchall()
            columns=[c_name[0] for c_name in cursor.description]
            data=pd.DataFrame(data,columns=columns)
            return data
        finally:
            conn.close()
    else:
        return pd.DataFrame()

print("All packages loaded successfully!")

#streamlit UI

st.set_page_config(page_title="🚓 SecureCheck: Police Post Dashboard", layout="wide")
st.title("🚓 SecureCheck: Police Post Dashboard")

#sidebar

menu = st.sidebar.selectbox(
    "Navigate",
    ["Home", "View logs","Add Logs"]
)

#Home page

#Title and description

if menu == "Home":
    st.subheader("Welcome to SecureCheck ✅")
    st.markdown("""
    🔐 **SecureCheck** is a data-driven platform built for evaluating traffic stop outcomes and trends.  
    Here's what you can do:
    - 📊 View detailed traffic stop records
    - 🚗 Analyze violation patterns by category
    - ⏱️ Review stop durations and officer performance
    - 📍 Visualize trends over time and location
    """)
    st.success("Let's make policing smarter and safer! 🚓")

#metics

    st.header("📊Key Metrics")
    query="select * from policedb.logs"
    data=fetch_data(query)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_stops=data.shape[0]
        st.metric("🚓 Total Police Stops", total_stops)

    with col2:
            
        arrests = data[data["stop_outcome"].str.contains("arrest", case=False, na=False)].shape[0]
        st.metric("🚨 Total Arrests", arrests)

    with col3:
        warnings = data[data["stop_outcome"].str.contains("Warning", case=False, na=False)].shape[0]
        st.metric("⚠️ Total Warnings", warnings)

    with col4:
        drug_stop = data[data["drugs_related_stop"] == 1].shape[0]
        st.metric("💊 Drug Related Stops", drug_stop)

#display logs

    st.header("📋Police Logs Overview")
    query="select * from policedb.logs"
    data=fetch_data(query)
    st.dataframe(data,use_container_width=True)
    st.markdown("---")  
    
#description 

    st.subheader("📝 Description")
    st.markdown("""
    The table above showcases daily police log records, including incident types, dates, and locations.
    - **Traffic Violation**: Involves offenses like speeding, illegal parking, or reckless driving.
    - **drug**: Incidents related to drug or unauthorized access.
    """)
    st.write("Analyzing this data helps identify areas with frequent incidents and peak hours, supporting smarter police response strategies.")
    st.subheader("📊 Visual Insights")      

    tab = st.tabs(['Stops By Violations', 'Driver Gender Distribution'])

 # SQL Query to fetch violation and its counts

    with tab[0]:
   
        query = "select violation, count(violation) as counts from policedb.logs group by violation"
        data = fetch_data(query)
        st.dataframe(data)

        fig, ax = plt.subplots(figsize=(4, 2.5))
        ax.bar(data['violation'], data['counts'], color='red', width=0.5)
        ax.set_xlabel("Violation", fontsize=5)
        ax.set_ylabel("Number of Violations", fontsize=5)
        ax.set_title("Violation Frequency", fontsize=5)
        ax.tick_params(axis='x', labelsize=4, rotation=45)
        ax.tick_params(axis='y', labelsize=4)
        st.pyplot(fig)

 # SQL Query to fetch Gender of Driver and its counts

    with tab[1]:
   
        query = "select driver_gender, count(*) as count from policedb.logs group by driver_gender"
        data = fetch_data(query)
        st.dataframe(data)

        fig, ax = plt.subplots(figsize=(4, 2.5)) 
        ax.bar(data['driver_gender'], data['count'], color='blue', width=0.5)
        ax.set_xlabel("Driver Gender", fontsize=5)
        ax.set_ylabel("Number of Male and Female", fontsize=5)
        ax.set_title("Gender Distribution", fontsize=5)
        ax.tick_params(axis='x', labelsize=4)
        ax.tick_params(axis='y', labelsize=4)
        st.pyplot(fig)
    st.markdown("---")
    st.markdown("❤️Built for Law enforcement by Securecheck")

#View Logs Page

elif menu=="View logs":

#view vehicle logs with filters

    st.subheader("📋View vechicle logs with filters")

    st.write("Use the filters to narrow down the logs")

    vehicle_input=st.text_input("🔍 Search by Vehicle Number")
    violation_input=st.text_input("🔍 Search by Violation")
    country_input=st.text_input("🔍 Search by Country")
   
    query = "SELECT * FROM policedb.logs WHERE 1=1"

    if vehicle_input:
        query += f" AND vehicle_number LIKE '%{vehicle_input}%'"

    if violation_input:
        query += f" AND violation LIKE '%{violation_input}%'"

    if country_input:
        query += f" AND country_name LIKE '%{country_input}%'"

    data=fetch_data(query)

    if not data.empty:
        if 'stop_time' in data.columns:
            data['stop_time'] = data['stop_time'].apply(lambda x: str(x).split()[-1] if pd.notnull(x) else '')

        st.success(f"✅ Showing {len(data)} matching logs")
        st.dataframe(data)
    else:
        st.warning("⚠️ No matching logs found.")
    
    st.markdown("---")  
    
#view log insights

    st.subheader("🧠 View logs insights")

    analysis_option = st.selectbox(
        "Choose 🚗 Vehicle/🧍Demographic/ 🕒 Time & Duration/ ⚖️ Violation-Based analysis to run:",
        [
            "Top 10 vehicle_Number involved in Drug-Related Stops",
            "Most Frequently Searched Vehicles",
            "Driver Age Group with Highest Arrest Rate",
            "Gender Distribution of Drivers Stopped in each Country",
            "Race & Gender Combination with Highest Search Rate",
            "Time of Day with Most Traffic Stops",
            "Average Stop Duration for different Violations",
            "Night Stops More Likely to Lead to Arrests",
            "Violations Most Associated with Searches or Arrests",
            "Most Common Violations for Young Drivers Under 25",
            "Violation Rarely Resulting in Search or Arrest",
            "Countries Report with Highest Drug-Related Stop Rates",
            "Arrest Rate by Country & Violation",
            "Country has the Most Stops with Search Conducted",
            "Yearly Breakdown of Stops and Arrests by Country",
            "Driver Violation Trends by Age & Race",
            "Time Period Analysis of Stops, Number of Stops by Year, Month, Hour of the Day",
            "Violations with High Search & Arrest Rates",
            "Driver Demographics by Country (Age, Gender and Race)",
            "Top 5 Violations with Highest Arrest Rates"
        ]
    )

    query_map={
        "Top 10 vehicle_Number involved in Drug-Related Stops": """ SELECT VEHICLE_NUMBER,COUNT(*) AS TOTAL_STOPS
                                                                    FROM POLICEDB.LOGS
                                                                    WHERE DRUGS_RELATED_STOP
                                                                    GROUP BY VEHICLE_NUMBER
                                                                    LIMIT 10; """,
        "Most Frequently Searched Vehicles": """ SELECT VEHICLE_NUMBER,COUNT(*) AS TOTAL_SEARCHS
                                                 FROM POLICEDB.LOGS
                                                 WHERE SEARCH_TYPE != "NO SEARCH"
                                                 GROUP BY VEHICLE_NUMBER
                                                 ORDER BY  VEHICLE_NUMBER DESC
                                                 LIMIT 10; """,
        "Driver Age Group with Highest Arrest Rate": """ SELECT
                                                            CASE
                                                               WHEN driver_age < 18 THEN 'Under 18'
                                                               WHEN driver_age BETWEEN 18 AND 25 THEN '18-25'
                                                               WHEN driver_age BETWEEN 26 AND 40 THEN '26-40'
                                                               WHEN driver_age BETWEEN 41 AND 60 THEN '41-60'
                                                               ELSE '60+'
                                                            END AS age_group,
                                                            COUNT(*) AS arrest_count
                                                            FROM POLICEDB.LOGS
                                                            WHERE stop_outcome = 'Arrest'
                                                            GROUP BY age_group
                                                            ORDER BY arrest_count DESC; """,
        "Gender Distribution of Drivers Stopped in each Country": """ SELECT COUNTRY_NAME,DRIVER_GENDER,COUNT(*) AS COUNT
                                                                      FROM POLICEDB.LOGS
                                                                      GROUP BY COUNTRY_NAME,DRIVER_GENDER
                                                                      ORDER BY COUNTRY_NAME; """,
        "Race & Gender Combination with Highest Search Rate": """SELECT DRIVER_RACE,DRIVER_GENDER,COUNT(*) AS STOP_COUNT
                                                                 FROM POLICEDB.LOGS
                                                                 WHERE SEARCH_TYPE != "No Search"
                                                                 GROUP BY DRIVER_RACE,DRIVER_GENDER
                                                                 ORDER BY STOP_COUNT DESC;
                                                                 LIMIT 1; """,
        "Time of Day with Most Traffic Stops": """SELECT HOUR(STOP_TIME) AS STOP_HOUR,COUNT(*) AS COUNT
                                                 FROM POLICEDB.LOGS
                                                 GROUP BY STOP_HOUR
                                                 ORDER BY COUNT DESC; """,
        "Average Stop Duration for different Violations": """SELECT VIOLATION,AVG(STOP_DURATION) AS AVG_STOP_DURATION
                                                             FROM POLICEDB.LOGS
                                                             GROUP BY VIOLATION
                                                             ORDER BY AVG_STOP_DURATION DESC; """,
        "Night Stops More Likely to Lead to Arrests": """SELECT 
	                                                     CASE 
		                                                     WHEN HOUR(STOP_TIME) BETWEEN 20 AND 23 
                                                             OR HOUR(STOP_TIME) BETWEEN 0 AND 5 THEN 'NIGHT'
		                                                     ELSE 'DAY'
		                                                     END AS TIME_OF_THE_DAY, 
                                                             COUNT(*) AS STOP_COUNTS,
                                                             SUM(CASE WHEN IS_ARRESTED = 1 THEN  1 ELSE 0 END) AS TOTAL_ARREST,
		                                                     ROUND(SUM(CASE WHEN IS_ARRESTED = 1 THEN  1 ELSE 0 END) * 100.0/COUNT(*),2) AS TOTAL_ARREST_PERCENTAGE
                                                         FROM POLICEDB.LOGS
                                                         GROUP BY TIME_OF_THE_DAY
                                                         ORDER BY TOTAL_ARREST_PERCENTAGE DESC; """,
        "Violations Most Associated with Searches or Arrests": """SELECT VIOLATION,SUM(CASE WHEN IS_ARRESTED = 1 THEN 1 ELSE 0 END) AS TOTAL_ARRESTED,
                                                                  SUM(CASE WHEN SEARCH_CONDUCTED = 1 THEN 1 ELSE 0 END) AS TOTAL_SEARCH_CONDUCTED,
                                                                  SUM(CASE WHEN IS_ARRESTED = 1 OR SEARCH_CONDUCTED = 1 THEN 1 ELSE 0 END) AS SEARCH_OR_ARREST
                                                                  FROM POLICEDB.LOGS
                                                                  GROUP BY VIOLATION
                                                                  ORDER BY SEARCH_OR_ARREST DESC """,
        "Most Common Violations for Young Drivers Under 25":""" SELECT violation, COUNT(*) AS count
                                                                FROM traffic_stops
                                                                WHERE driver_age < 25
                                                                GROUP BY violation
                                                                ORDER BY count DESC; """,
        "Violation Rarely Resulting in Search or Arrest":""" SELECT VIOLATION,
                                                             SUM(CASE WHEN IS_ARRESTED = 1 THEN 1 ELSE 0 END) AS TOTAL_ARRESTED,
                                                             SUM(CASE WHEN SEARCH_CONDUCTED = 1 THEN 1 ELSE 0 END) AS TOTAL_SEARCH_CONDUCTED,
                                                             SUM(CASE WHEN IS_ARRESTED = 1 OR SEARCH_CONDUCTED = 1 THEN 1 ELSE 0 END) AS SEARCH_OR_ARREST
                                                             FROM POLICEDB.LOGS
                                                             GROUP BY VIOLATION
                                                             ORDER BY SEARCH_OR_ARREST 
                                                             LIMIT 1; """,
        "Countries Report with Highest Drug-Related Stop Rates": """ SELECT COUNTRY_NAME,
                                                                     SUM(CASE WHEN DRUGS_RELATED_STOP =1 THEN 1 ELSE 0 END) AS DRUG_RELATED_STOPS,
                                                                     ROUND(SUM(CASE WHEN DRUGS_RELATED_STOP =1 THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS PERCENTAGE_OF_DRUG_RELATED_STOPS
                                                                     FROM POLICEDB.LOGS
                                                                     GROUP BY COUNTRY_NAME
                                                                     ORDER BY PERCENTAGE_OF_DRUG_RELATED_STOPS; """,
        "Arrest Rate by Country & Violation":"""SELECT COUNTRY_NAME,
                                                VIOLATION,
                                                ROUND(SUM(CASE WHEN IS_ARRESTED=1 THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS ARREST_RATE
                                                FROM POLICEDB.LOGS
                                                GROUP BY COUNTRY_NAME,VIOLATION
                                                ORDER BY COUNTRY_NAME; """,
        "Country has the Most Stops with Search Conducted": """ SELECT COUNTRY_NAME,COUNT(*)AS COUNT
                                                                FROM POLICEDB.LOGS
                                                                WHERE SEARCH_CONDUCTED=1
                                                                GROUP BY COUNTRY_NAME
                                                                ORDER BY COUNT DESC
                                                                LIMIT 1; """,
        "Yearly Breakdown of Stops and Arrests by Country": """ SELECT COUNTRY_NAME,STOP_YEAR,TOTAL_STOP,TOTAL_ARREST,
                                                                ROUND(TOTAL_ARREST * 100.0 / TOTAL_STOP,2),
                                                                RANK() OVER(PARTITION BY STOP_YEAR ORDER BY TOTAL_ARREST DESC) AS ARREST_RANK_IN_YEAR
                                                                FROM
                                                                (SELECT COUNTRY_NAME,YEAR(STOP_TIME) AS STOP_YEAR,COUNT(*) AS TOTAL_STOP,
                                                                 SUM(CASE WHEN IS_ARRESTED = 1 THEN 1 ELSE 0 END) AS TOTAL_ARREST
                                                                 FROM POLICEDB.LOGS
                                                                 GROUP BY COUNTRY_NAME,STOP_YEAR
                                                                 ORDER BY STOP_YEAR
                                                                ) AS YEARLY_STATS;""",
        "Driver Violation Trends by Age & Race": """ SELECT DRIVER_RACE,VIOLATION,AGE_GROUP,COUNT(*) AS STOP_COUNT 
                                                      FROM
                                                      (SELECT DRIVER_RACE,VIOLATION,
                                                      CASE
	                                                  WHEN DRIVER_AGE < 18 THEN 'UNDER 18'
                                                      WHEN DRIVER_AGE BETWEEN 18 AND 25 THEN '18-25'
	                                                  WHEN DRIVER_AGE BETWEEN 26 AND 40 THEN '26-40'
	                                                  WHEN DRIVER_AGE BETWEEN 41 AND 60 THEN '41-60'
	                                                  ELSE'ABOVE 60'
                                                      END AS AGE_GROUP
                                                      FROM POLICEDB.LOGS) AS SUB
                                                    GROUP BY DRIVER_RACE,VIOLATION,AGE_GROUP
                                                    ORDER BY STOP_COUNT DESC;""",
        "Time Period Analysis of Stops, Number of Stops by Year, Month, Hour of the Day": """ SELECT EXTRACT(YEAR FROM STOP_DATE) AS YEAR,
                                                                                              EXTRACT(MONTH FROM STOP_DATE) AS MONTH,
                                                                                              EXTRACT(HOUR FROM STOP_TIME) AS HOUR,
                                                                                              COUNT(*) AS TOTAL_STOPS
                                                                                              FROM POLICEDB.LOGS
                                                                                              GROUP BY YEAR,MONTH,HOUR
                                                                                              ORDER BY YEAR;""",
        "Violations with High Search & Arrest Rates":"""SELECT VIOLATION,TOTAL_STOP,TOTAL_ARREST,TOTAL_SEARCH,
                                                        ROUND(100*(TOTAL_ARREST/ TOTAL_STOP), 2) AS ARREST_RATE,
                                                        ROUND(100*(TOTAL_SEARCH / TOTAL_STOP), 2) AS SEARCH_RATE,
                                                        RANK() OVER (ORDER BY (TOTAL_ARREST * 1.0 / TOTAL_STOP) DESC) AS ARREST_RANK,
                                                        RANK() OVER (ORDER BY (TOTAL_SEARCH * 1.0 / TOTAL_STOP) DESC) AS SEARCH_RANK
                                                        FROM (
                                                        SELECT VIOLATION,COUNT(*) AS TOTAL_STOP,
                                                        SUM(CASE WHEN IS_ARRESTED = 1 THEN 1 ELSE 0 END) AS TOTAL_ARREST,
                                                        SUM(CASE WHEN SEARCH_CONDUCTED = 1 THEN 1 ELSE 0 END) AS TOTAL_SEARCH
                                                        FROM POLICEDB.LOGS
                                                        GROUP BY VIOLATION;) AS LOGS
                                                        ORDER BY ARREST_RANK ASC,SEARCH_RANK ASC;""",
        "Driver Demographics by Country (Age, Gender and Race)":""" SELECT 
                                                                    COUNTRY_NAME,CASE
                                                                    WHEN DRIVER_AGE < 18 THEN 'UNDER 18'
                                                                    WHEN DRIVER_AGE BETWEEN 18 AND 25 THEN '18-25'
                                                                    WHEN DRIVER_AGE BETWEEN 26 AND 40 THEN '26-40'
                                                                    WHEN DRIVER_AGE BETWEEN 41 AND 60 THEN '41-60'
                                                                    ELSE'ABOVE 60'
                                                                    END AS AGE_GROUP,
                                                                    DRIVER_GENDER,DRIVER_RACE,COUNT(*)AS TOTAL_COUNT
                                                                    FROM POLICEDB.LOGS
                                                                    GROUP BY COUNTRY_NAME,AGE_GROUP,DRIVER_GENDER,DRIVER_RACE
                                                                    ORDER BY COUNTRY_NAME,AGE_GROUP,DRIVER_GENDER,DRIVER_RACE;""",
        "Top 5 Violations with Highest Arrest Rates":""" SELECT VIOLATION,TOTAL_ARREST,ARREST_RATE
                                                         FROM (
                                                         SELECT VIOLATION,COUNT(*) AS TOTAL_STOP,SUM(CASE WHEN IS_ARRESTED = 1 THEN 1 ELSE 0 END) AS TOTAL_ARREST,
                                                         ROUND(100.0 * SUM(CASE WHEN IS_ARRESTED = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS ARREST_RATE
                                                         FROM POLICEDB.LOGS
                                                         GROUP BY VIOLATION
                                                         ) AS ARREST_LOGS
                                                        ORDER BY ARREST_RATE DESC;"""   
    }
    result=pd.DataFrame()
   
    if st.button("Run Analysis"):
        query=query_map.get(analysis_option)
    if query:
        result=fetch_data(query)
# display results

    if not result.empty:
        st.write(result)
    else:
        st.warning("No Results Found")

    st.markdown("---") 
    st.markdown("❤️Built for Law enforcement by Securecheck")
#Add logs page

elif menu=="Add Logs":

#use natural filters to analyse stops and trends

    st.subheader("🔍 Use natural language to filter past police stops and analyze trends.")
    st.markdown("📝 Fill in the details below to log a police stop and get a predicted outcome & violation.")

    query = "select * from policedb.logs"
    data = fetch_data(query)

    predicted_outcome = "Warning"   
    predicted_violation = "Speeding"

    with st.form("new_log_form"):
        vehicle_number = st.text_input("Vehicle Number")
        country_name = st.selectbox("Country Name", ["Canada", "USA", "India"])
        driver_gender = st.radio("Gender", ["Male", "Female"])
        driver_age = st.number_input("Age", min_value=18, max_value=100, value=20)
        driver_race = st.selectbox("Race", ["Asian", "Black", "White", "Hispanic", "Other"])
        search_type = st.selectbox("Search Type", ["Vehicle Search", "Frisk", "No Search"])
        stop_outcome = st.selectbox("Stop Outcome", ["Arrest", "Ticket", "Warning"])
        search_conducted = st.selectbox("Was a Search Conducted?", ["0", "1"])
        stop_date = st.date_input("Stop Date")
        stop_time = st.time_input("Stop Time")
        drugs_related_stop = st.selectbox("Was it drug related?", ["0", "1"])
        submitted = st.form_submit_button("✅ Predict Stop Outcome & Violation")

    if submitted:
# convert stop_time to string for comparison
        stop_time_str = stop_time.strftime('%H:%M:%S')  

        filtered_data = data[
            (data["driver_gender"] == driver_gender) &
            (data["driver_age"] == driver_age) &
            (data['search_conducted'] == int(search_conducted)) &
            (data['stop_time'] == stop_time_str) &
            (data['drugs_related_stop'] == int(drugs_related_stop))
        ]

        if not filtered_data.empty:
            predicted_outcome = filtered_data["stop_outcome"].mode()[0]
            predicted_violation = filtered_data["violation"].mode()[0]

        search_text = "A search was conducted" if int(search_conducted) else "No search was conducted"
        drug_text = "was drug related" if int(drugs_related_stop) else "was not drug related"

        st.markdown("---")

#predicted summary
        st.subheader("🚓 **Prediction Summary**")

        st.markdown(f"""
            📝 A **{driver_age}**-year-old **{driver_gender}** driver in **{country_name}** 
            was stopped for **{predicted_violation}** at {stop_time.strftime('%I:%M %p')} on {stop_date}.
            **{search_text}**, received a **{predicted_outcome}**, and **{drug_text}**.
        """)
        st.markdown("---")
    st.markdown("---")
    st.markdown("❤️Built for Law enforcement by Securecheck")

