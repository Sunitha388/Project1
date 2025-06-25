import streamlit as st  # ibrary for creating web app UI
import mysql.connector  # Importing MySQL connector to connect to MySQL database
import pandas as pd     # data handling and manipulation

#  Establish connection to the MySQL database
connection = mysql.connector.connect(
    host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",  
    port=4000,                                            
    user="2LwupNhEckogWnm.root",                             
    password="oHH2C3xTDDLFymia",                           
    database="imdb_movies",                                 
)

cursor = connection.cursor()                # Create a cursor object to execute SQL queries
cursor.execute("SELECT * FROM Movies;")     # SQL query to get all rows from 'Movies' table
rows = cursor.fetchall()                    # Fetch all resulting rows from the executed query


#  Load IMDb movie dataset from a CSV file
df = pd.read_csv("file_imdb.csv")          

#  Data Preparation
df['Duration_Hrs'] = (df['Duration(in_mins)'] / 60).round(2)  # Convert duration from minutes to hours, round to 2 decimal places
df['Votes'] = df['Votes'].astype(int)                         # Ensure 'Votes' column is of integer type

# -------- SIDEBAR NAVIGATION --------
st.title(' Welcome to the IMDb Streamlit Dashboard!')


st.sidebar.title("🎬 IMDb Dashboard")

choice = st.sidebar.selectbox("Go to", [ "Filtering", "Visualization"])


if choice == 'Filtering':
    st.title(" IMDb Movie Filter Dashboard")



# Duration filter (dropdown for movie duration)
duration_filter = st.sidebar.selectbox(
    "Select Duration (in Hours):",          # Label for the dropdown
    ("All", "< 2 hrs", "2–3 hrs", "> 3 hrs") # Options for movie durations
)

# IMDb Rating filter (slider to select minimum rating)
rating_filter = st.sidebar.slider("Minimum Rating:", min_value=0.0, max_value=10.0, value=5.0, step=0.1)

# Votes filter (number input to filter movies by minimum number of votes)
votes_filter = st.sidebar.number_input("Minimum Number of Votes:", min_value=0, value=1000, step=500)

# Genre filter (multiselect to select one or more genres)
genres = df['Genre'].dropna().str.split(', ').explode().unique()  # Extract unique genres from the dataset
genre_filter = st.sidebar.multiselect("Select Genre(s):", genres, default=[])  # Multi-select genre filter

#  Start filtering dataset based on user selections
filtered_df = df.copy()   # Start with full dataset and apply filters step-by-step

# Filter by Duration (in Hours)
if duration_filter == "< 2 hrs":
    filtered_df = filtered_df[filtered_df['Duration_Hrs'] < 2]
elif duration_filter == "2–3 hrs":
    filtered_df = filtered_df[(filtered_df['Duration_Hrs'] >= 2) & (filtered_df['Duration_Hrs'] <= 3)]
elif duration_filter == "> 3 hrs":
    filtered_df = filtered_df[filtered_df['Duration_Hrs'] >3]

# Filter by IMDb Rating
filtered_df = filtered_df[filtered_df['Rating'] >= rating_filter]

# Filter by Number of Votes
filtered_df = filtered_df[filtered_df['Votes'] >= votes_filter]

# Filter by Genre (if any genres are selected)
if genre_filter:
    filtered_df = filtered_df[filtered_df['Genre'].apply(lambda x: any(g in x for g in genre_filter))]

#  Display Results Section
st.subheader(f"🎥 Filtered Movies ({len(filtered_df)}) Results")  # Display count of filtered movies

#  Safely display dataframe if columns exist
expected_cols = ['Title', 'Duration(in_mins)', 'Rating', 'Votes', 'Genre']  # Expected columns for display
existing_cols = [col for col in expected_cols if col in filtered_df.columns] # Verify which of those columns actually exist

if filtered_df.empty:                      # If no rows match the filters
    st.warning("No data to display after applying filters.")
else:
    st.dataframe(filtered_df[existing_cols])  # Display the filtered dataset in a nice table format
    

# completed clean
cursor.close()
connection.close() 
    
    
# NXT IS VISUALIZATION 


import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns

connection = mysql.connector.connect(
    host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    port=4000,
    user="2LwupNhEckogWnm.root",
    password="oHH2C3xTDDLFymia",
    database="imdb_movies",
)
cursor = connection.cursor()


if  choice == 'Visualization':
    st.title(" ***IMDb Movie Visualizations***")

     # Fetch the data again (or reuse if already fetched)
    cursor = connection.cursor()
    query = "SELECT * FROM Movies"
    cursor.execute(query)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=["MovieID", "Title", "Rating", "Votes", "Duration", "Genre"]) 

    # Genre Distribution Bar Chart
    st.subheader(" Genre Distribution")

    genre_counts = df["Genre"].value_counts()
    fig5, ax5 = plt.subplots()
    sns.barplot(x=genre_counts.index, y=genre_counts.values, palette="pastel", ax=ax5)
    ax5.set_xlabel("Genre")
    ax5.set_ylabel("Number of Movies")
    ax5.set_title("Number of Movies per Genre")
    ax5.tick_params(axis='x', rotation=45)
    st.pyplot(fig5)

    st.markdown(" Rating Distribution")
    fig, ax = plt.subplots()
    sns.histplot(df["Rating"], bins=10, kde=True, ax=ax)
    ax.set_xlabel("IMDb Rating")
    ax.set_ylabel("Count of Movies")
    st.pyplot(fig)

    st.markdown(" Voting Trends by Genre")

    # Calculate average votes per genre
    avg_votes_per_genre = df.groupby("Genre")["Votes"].mean().sort_values(ascending=False)

    # Bar Chart
    fig, ax = plt.subplots()
    sns.barplot(x=avg_votes_per_genre.index, y=avg_votes_per_genre.values, ax=ax)
    ax.set_xlabel("Genre")
    ax.set_ylabel("Average Votes")
    plt.xticks(rotation=45)

    # Show plot in Streamlit
    st.pyplot(fig)


    st.markdown(" Rating Trends by Genre")

    avg_ratings_per_genre = df.groupby("Genre")[["Rating"]].mean()
    
    #  Create a Heatmap-friendly format (Genres as Rows)
    pivot_df = avg_ratings_per_genre.T  # Transpose for heatmap

    # Heatmap Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(pivot_df, annot=True, cmap="coolwarm", fmt=".1f", linewidths=0.5, ax=ax)

    ax.set_xlabel("Genre")
    ax.set_ylabel("Average Rating")
    plt.xticks(rotation=45)

    # Show plot in Streamlit
    st.pyplot(fig)
    
    #for duration 
    st.markdown(" Average Duration by Genre")

    avg_duration_per_genre = df.groupby("Genre")["Duration"].mean().sort_values(ascending=False)

    # Plot Bar Chart
    st.bar_chart(avg_duration_per_genre,horizontal=True)
    
    
    #top 10 Movies by Rating and Voting Counts-- Identify movies with the highest ratings and voting engagement.
    # Section Title
    st.markdown(" Top 10 Movies by Rating & Voting Counts")

    # Filter movies with high ratings and  votes
    top_movies = df.sort_values(["Rating", "Votes"], ascending=[False, False]).head(10)

    # Display as a Table
    st.dataframe(top_movies[["Title", "Rating", "Votes"]])
    
    
    #Genre-Based Rating Leaders: Highlight the top-rated movie for each genre in a table.
    st.markdown(" Genre-Based Rating Leaders")

    # Get the top-rated movie per genre
    top_movies_per_genre = df.loc[df.groupby("Genre")["Rating"].idxmax()]

    # Sort genres by rating
    top_movies_per_genre = top_movies_per_genre.sort_values("Rating", ascending=False)

    # Display table
    st.dataframe(top_movies_per_genre[["Genre", "Title", "Rating"]])
    
    
    # Most Popular Genres by Voting: Identify genres with the highest  voting counts in a pie chart.
    st.markdown(" Most Popular Genres by Voting")

    # Group by Genre and sum total votes
    genre_votes = df.groupby("Genre")["Votes"].sum().sort_values(ascending=False)

    # Plot Pie Chart
    fig, ax = plt.subplots()
    ax.pie(genre_votes, labels=genre_votes.index, autopct="%1.1f%%", startangle=140,
    colors=plt.cm.Paired.colors, wedgeprops={"edgecolor": "black"})

    # Display in Streamlit
    st.pyplot(fig)

    #   shortest and longest movies.
    st.markdown(" Duration Extremes: Shortest & Longest Movies")

    # Sort by Duration
    df_sorted = df.sort_values(by="Duration", ascending=True)

    # Get shortest and longest movie
    shortest_movie = df_sorted.iloc[0]  # First row (smallest duration)
    longest_movie = df_sorted.iloc[-1]  # Last row (largest duration)

    # display long and short movie
    duration_extremes = pd.DataFrame([shortest_movie, longest_movie])

    # Rename index clear understanding
    duration_extremes.index = ["Shortest Movie", "Longest Movie"]

    # Display result
    st.dataframe(duration_extremes[["Title", "Genre", "Duration"]])

    # Correlation Analysis: Analyze the relationship between ratings and voting counts using a scatter plot.
    st.markdown(" Correlation Analysis")

    # Create scatter plot
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.scatterplot(data=df, x="Rating", y="Votes", alpha=0.5, ax=ax)
    ax.set_title("Ratings vs. Voting Counts")
    ax.set_xlabel("Rating")
    ax.set_ylabel("Votes  ")
    ax.set_yscale("log")  # Use log scale for better visualization
    # Show in Streamlit
    st.pyplot(fig)



    # Close connection
    cursor.close()
    connection.close()

