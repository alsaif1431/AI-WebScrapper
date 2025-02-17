# 1. Create a virtual environment
python -m venv venv

# 2. Activate the virtual environment
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

#if there are any errors in the instalation please install every library in the requirements.txt


# 4. *********     IMPORTANT     ********
        1. **[Create a free Supabase account](https://supabase.com/)**.
        2. **Create a new project** inside Supabase.
        3. **Create a table** in your project by running the following SQL command in the **SQL Editor**:
        
        ```sql
        CREATE TABLE IF NOT EXISTS scraped_data (
        id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        unique_name TEXT NOT NULL,
        url TEXT,
        raw_data JSONB,        
        formatted_data JSONB, 
        pagination_data JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW()
        );
        ```

        4. **Go to Project Settings → API** and copy:
            - **Supabase URL**
            - **Anon Key**
        
        5. **Update your `.env` file** with these values:
        
        ```
        SUPABASE_URL=your_supabase_url_here
        SUPABASE_ANON_KEY=your_supabase_anon_key_here
        ```

        6. **Restart the project** and you’re good to go! 🚀


## 5. run "playwright install"

## 6. add your api keys in .env files for the models (you can also add them in the app)

## 7. type the command "streamlit run streamlit_app.py" in your project terminal

## 8. Enjoy the working app