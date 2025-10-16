from app import create_app
from app.models1 import db
from sqlalchemy import text

app = create_app()

def analyze_database():
    with app.app_context():
        try:
            print("🔍 ANALIZANDO BASE DE DATOS COMPLETA...")
            print("=" * 50)
            
            # Obtener TODAS las tablas
            result = db.session.execute(text("SHOW TABLES"))
            all_tables = [row[0] for row in result]
            
            print(f"📊 TOTAL DE TABLAS ENCONTRADAS: {len(all_tables)}")
            print("=" * 50)
            
            # Analizar cada tabla
            for table in sorted(all_tables):
                try:
                    # Contar registros
                    count_result = db.session.execute(text(f"SELECT COUNT(*) FROM `{table}`"))
                    count = count_result.scalar()
                    
                    # Obtener estructura
                    structure_result = db.session.execute(text(f"DESCRIBE `{table}`"))
                    columns = [row[0] for row in structure_result]
                    
                    print(f"\n📋 TABLA: {table}")
                    print(f"   📈 Registros: {count}")
                    print(f"   🏗️  Columnas: {', '.join(columns)}")
                    
                    # Mostrar algunos datos de ejemplo (solo para tablas con datos)
                    if count > 0 and count <= 10:
                        sample_result = db.session.execute(text(f"SELECT * FROM `{table}` LIMIT 3"))
                        sample_data = sample_result.fetchall()
                        print(f"   📝 Ejemplo de datos:")
                        for i, row in enumerate(sample_data):
                            print(f"      {i+1}. {row}")
                    
                except Exception as e:
                    print(f"   ❌ Error analizando {table}: {e}")
            
            print("\n" + "=" * 50)
            print("🎯 TABLAS DUPLICADAS/PROBLEMÁTICAS IDENTIFICADAS:")
            
            # Identificar duplicados
            table_groups = {}
            for table in all_tables:
                base_name = table.rstrip('s')  # Remover 's' final
                if base_name not in table_groups:
                    table_groups[base_name] = []
                table_groups[base_name].append(table)
            
            for base_name, tables in table_groups.items():
                if len(tables) > 1:
                    print(f"   ⚠️  {base_name}: {tables}")
            
        except Exception as e:
            print(f"❌ Error general: {e}")

if __name__ == '__main__':
    analyze_database()
