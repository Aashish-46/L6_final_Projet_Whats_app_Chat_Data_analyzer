import os
import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns

# Add logo image path
logo_image = "logo.png"

# Display the logo image
st.sidebar.image(logo_image, use_column_width=True)

st.sidebar.title("WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    file_extension = os.path.splitext(uploaded_file.name)[1]
    if file_extension.lower() != ".txt":
        st.sidebar.error("Invalid file format. Please upload a TXT file.")
    else:
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
        try:
            df = preprocessor.preprocess(data)

            # Check if the file is appropriate for analysis
            if len(df) == 0:
                st.sidebar.error("Please upload a TXT file exported from WhatsApp.")
            else:
                # fetch unique users
                user_list = df['user'].unique().tolist()
                user_list.sort()
                user_list.insert(0, "Overall")

                selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

                if st.sidebar.button("Show Analysis"):
                    # Stats Area
                    num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
                    st.title("Top Statistics")
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.header("Total Messages")
                        st.title(num_messages)
                    with col2:
                        st.header("Total Words")
                        st.title(words)
                    with col3:
                        st.header("Media Shared")
                        st.title(num_media_messages)
                    with col4:
                        st.header("Links Shared")
                        st.title(num_links)

                    # Monthly timeline
                    st.title("Monthly Timeline")
                    timeline = helper.monthly_timeline(selected_user, df)
                    fig, ax = plt.subplots()
                    ax.plot(timeline['time'], timeline['message'], color='green')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)

                    # Daily timeline
                    st.title("Daily Timeline")
                    daily_timeline = helper.daily_timeline(selected_user, df)
                    fig, ax = plt.subplots()
                    ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)

                    # Activity map
                    st.title('Activity Map')
                    col1, col2 = st.columns(2)

                    with col1:
                        st.header("Most busy day")
                        busy_day = helper.week_activity_map(selected_user, df)
                        fig, ax = plt.subplots()
                        ax.bar(busy_day.index, busy_day.values, color='purple')
                        plt.xticks(rotation='vertical')
                        st.pyplot(fig)

                    with col2:
                        st.header("Most busy month")
                        busy_month = helper.month_activity_map(selected_user, df)
                        fig, ax = plt.subplots()
                        ax.bar(busy_month.index, busy_month.values, color='orange')
                        plt.xticks(rotation='vertical')
                        st.pyplot(fig)

                    st.title("Weekly Activity Map")
                    user_heatmap = helper.activity_heatmap(selected_user, df)
                    fig, ax = plt.subplots()
                    ax = sns.heatmap(user_heatmap)
                    st.pyplot(fig)

                    # Finding the busiest users in the group (Group level)
                    if selected_user == 'Overall':
                        st.title('Most Busy Users')
                        x, new_df = helper.most_busy_users(df)
                        fig, ax = plt.subplots()

                        col1, col2 = st.columns(2)

                        with col1:
                            ax.bar(x.index, x.values, color='red')
                            plt.xticks(rotation='vertical')
                            st.pyplot(fig)
                        with col2:
                            st.dataframe(new_df)

                    # WordCloud
                    st.title("Wordcloud")
                    df_wc = helper.create_wordcloud(selected_user, df)
                    fig, ax = plt.subplots()
                    ax.imshow(df_wc)
                    st.pyplot(fig)

                    # Most common words
                    most_common_df = helper.most_common_words(selected_user, df)

                    fig, ax = plt.subplots()
                    ax.barh(most_common_df[0], most_common_df[1])
                    plt.xticks(rotation='vertical')

                    st.title('Most Common Words')
                    st.pyplot(fig)

                    # Emoji analysis
                    emoji_df = helper.emoji_helper(selected_user, df)
                    st.title("Emoji Analysis")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.dataframe(emoji_df)

                    if not emoji_df.empty:  # Check if the DataFrame is empty
                        with col2:
                            fig, ax = plt.subplots()
                            ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
                            st.pyplot(fig)
                    else:
                        st.warning("No emoji data available for the selected user.")
        except ValueError as e:
            st.sidebar.error(str(e))
else:
    st.sidebar.info("Please upload a TXT file exported from WhatsApp.")
