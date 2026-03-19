import sqlite3
con = sqlite3.connect('gym.db')
rows = con.execute("SELECT id, precio_total, pagado, pendiente FROM suscripciones ORDER BY id DESC LIMIT 5").fetchall()
for r in rows: print(r)
pagos = con.execute("SELECT * FROM pagos ORDER BY id DESC LIMIT 5").fetchall()
for p in pagos: print(p)
con.close()