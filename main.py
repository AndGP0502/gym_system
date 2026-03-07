from modulos.suscripciones import ver_estado_gimnasio, ver_clientes_vencidos


print("\nESTADO DEL GIMNASIO\n")

estado = ver_estado_gimnasio()

for fila in estado:
    
    print("\nCLIENTE | PLAN | VENCE | PAGADO | DEUDA")
    print("----------------------------------------")
    
    for fila in estado:
        print(f"{fila[0]} | {fila[1]} | {fila[2]} | {fila[3]} | {fila[4]}")
        
    
    print("\nCLIENTES VENCIDOS")
    print("-----------------")
    
    vencidos = ver_clientes_vencidos()
    
    for cliente in vencidos:
        print(f"{cliente[0]} - venció el {cliente[1]}")