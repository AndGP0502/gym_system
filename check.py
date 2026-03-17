import sqlite3
con = sqlite3.connect('gym.db')
rows = con.execute("""
    SELECT c.id, c.nombre 
    FROM clientes c 
    LEFT JOIN suscripciones s ON c.id = s.cliente_id 
    WHERE s.id IS NULL 
    ORDER BY c.id
""").fetchall()
print(f"Clientes sin suscripcion: {len(rows)}")
for r in rows:
    print(r)
con.close()
