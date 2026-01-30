



def leq_notes_structurer(
        df,
        id_column,
        note_column,
        server,
        database_path,
        database_table,
        llm_model,
):
    
    import lmstudio as lms
    import pandas as pd
    import json
    import re
    import sqlite3
    from tqdm import tqdm
        
    lms.configure_default_client(server)

    # --- DATABASE SETUP ---
    def init_db():
        """Creates the database_table if it doesn't exist."""
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        # We use id_orden as the PRIMARY KEY to prevent duplicates
        c.execute(f'''
            CREATE TABLE IF NOT EXISTS {database_table} (
                id_orden TEXT PRIMARY KEY,
                primary_status TEXT,
                is_ready BOOLEAN,
                confidence TEXT,
                reasoning TEXT,
                ts_status TEXT,
                anestesia_status TEXT,
                psico_status TEXT,
                sano_status TEXT,
                hospital_delay TEXT,
                raw_response TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_to_db(data):
        """Inserts a single row into the database."""
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        try:
            c.execute(f'''
                INSERT OR REPLACE INTO {database_table} VALUES 
                (:id_orden, :primary_status, :is_ready, :confidence, :reasoning, 
                :ts_status, :anestesia_status, :psico_status, :sano_status, 
                :hospital_delay, :raw_response)
            ''', data)
            conn.commit()
        except Exception as e:
            print(f"DB Error: {e}")
        finally:
            conn.close()

    def get_processed_ids():
        """Returns a set of IDs that are already finished."""
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        try:
            c.execute(f"SELECT id_orden FROM {database_table}")
            # Return a set for fast lookup
            return set(str(row[0]) for row in c.fetchall())
        except:
            return set()
        finally:
            conn.close()

    # --- PROCESSING LOGIC ---

    def clean_and_parse_json(response_text):
        # ... [KEEP YOUR EXISTING PARSING FUNCTION HERE] ...
        # (Copy the clean_and_parse_json function from the previous step)
        try:
            if "```" in response_text:
                response_text = response_text.split("```json")[-1].split("```")[0]
                if "```" in response_text:
                    response_text = response_text.split("```")[-1].split("```")[0]
            match = re.search(r'\{.*\}', response_text.strip(), re.DOTALL)
            if match:
                json_str = match.group()
            else:
                json_str = response_text.strip()
            return json.loads(json_str)
        except:
            return None

    def process_batch_sqlite(df, id_column, note_column):
        # 1. Initialize DB
        init_db()
        
        # 2. Check what is already done
        processed_ids = get_processed_ids()
        print(f"Found {len(processed_ids)} rows already processed in DB. Skipping them.")
        
        print("Starting connection to LM Studio...")
        with lms.Client() as client:
            model = client.llm.model(llm_model)
            
            # Iterate through the DataFrame
            for idx, row in tqdm(df.iterrows(), total=len(df)):
                current_id = str(row[id_column])
                
                # SKIP if already done
                if current_id in processed_ids:
                    continue
                
                note = row[note_column]
                
                try:
                    full_input = f"{note}"
                    result = model.respond(full_input)
                    parsed_data = clean_and_parse_json(result.content)
                    
                    if parsed_data:
                        # Prepare record for DB
                        record = {
                            'id_orden': current_id,
                            'primary_status': parsed_data.get('primary_status'),
                            'is_ready': parsed_data.get('is_ready'),
                            'confidence': parsed_data.get('confidence'),
                            'reasoning': parsed_data.get('reasoning'),
                            'ts_status': str(parsed_data.get('cq_compliance', {}).get('trabajo_social', '')),
                            'anestesia_status': str(parsed_data.get('cq_compliance', {}).get('anestesia', '')),
                            'psico_status': str(parsed_data.get('cq_compliance', {}).get('psicologia', '')),
                            'sano_status': str(parsed_data.get('cq_compliance', {}).get('sano', '')),
                            'hospital_delay': str(parsed_data.get('cq_compliance', {}).get('hospital_delay', '')),
                            'raw_response': None 
                        }
                        # SAVE IMMEDIATELY
                        save_to_db(record)
                    else:
                        # Save error state so we don't loop forever on bad data
                        error_record = {
                            'id_orden': current_id,
                            'primary_status': 'ERROR_PARSING', 
                            'is_ready': 0, 'confidence': 'Low', 'reasoning': 'JSON Fail',
                            'ts_status': '', 'anestesia_status': '', 'psico_status': '', 
                            'sano_status': '', 'hospital_delay': '', 
                            'raw_response': result.content
                        }
                        save_to_db(error_record)
                        
                except Exception as e:
                    print(f"API Error at ID {current_id}: {e}")
                    # Optional: Don't save to DB on API error so it retries next time


    # Assuming your DataFrame has columns 'id_orden' and 'estado_llamada'
    process_batch_sqlite(df, id_column=id_column, note_column=note_column)

    print("Processing complete. Loading data from DB...")