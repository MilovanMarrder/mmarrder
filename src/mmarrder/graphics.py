#------------------------------------
#    Gráficos personalizados        
#------------------------------------




# Luego pensar´en las categorías para ordenarlos mejor.

def distribucion_con_tabla_leyenda(
    df,
    columna_categoria,
    columna_grupo,
    orden_categorias=None,
    orden_grupos=None,
    paleta_colores=None,
    titulo='Distribución por Categoría',
    etiqueta_x='Categoría',
    etiqueta_y='Cantidad',
    mostrar_porcentaje=True,
    posicion_tabla='superior_derecha',
    figsize_aspect=2.2,
    figsize_height=5
):
    """
    Crea un gráfico de barras agrupadas con tabla de totales.
    Se aplica una tabla como leyenda indicando totales y porcentajes.
    
    Parámetros:
    -----------
    df : DataFrame
        DataFrame con los datos
    columna_categoria : str
        Nombre de la columna para el eje X 
    columna_grupo : str
        Nombre de la columna para agrupar por color 
    orden_categorias : list, opcional
        Orden personalizado para las categorías del eje X
    orden_grupos : list, opcional
        Orden personalizado para los grupos (colores)
    paleta_colores : dict, opcional
        Diccionario {grupo: color} para personalizar colores
    titulo : str
        Título del gráfico
    etiqueta_x : str
        Etiqueta del eje X
    etiqueta_y : str
        Etiqueta del eje Y
    mostrar_porcentaje : bool
        Si True, muestra columna de porcentaje en la tabla
    posicion_tabla : str
        'superior_derecha', 'superior_izquierda', 'inferior_derecha', 'inferior_izquierda'
    figsize_aspect : float
        Relación ancho/alto del gráfico
    figsize_height : float
        Altura del gráfico
    
    Retorna:
    --------
    matplotlib.figure.Figure
        Objeto de la figura de matplotlib
    """
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    # Configurar estilo
    sns.set_style("whitegrid")
    plt.rcParams['font.family'] = 'sans-serif'
    
    # Determinar orden de grupos si no se proporciona
    if orden_grupos is None:
        orden_grupos = df[columna_grupo].unique().tolist()
    
    # Determinar orden de categorías si no se proporciona
    if orden_categorias is None:
        orden_categorias = df[columna_categoria].unique().tolist()
    
    # Crear paleta de colores por defecto si no se proporciona
    if paleta_colores is None:
        colores_default = ['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4', 
                          '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', 
                          '#bcbd22', '#17becf']
        paleta_colores = {grupo: colores_default[i % len(colores_default)] 
                         for i, grupo in enumerate(orden_grupos)}
    
    # Calcular totales
    totales = df[columna_grupo].value_counts()
    total_general = len(df)
    
    # Crear el gráfico
    g = sns.catplot(
        data=df,
        x=columna_categoria,
        hue=columna_grupo,
        hue_order=orden_grupos,
        kind='count',
        aspect=figsize_aspect,
        height=figsize_height,
        palette=paleta_colores,
        legend=False,
        order=orden_categorias
    )
    
    # Configurar títulos y etiquetas
    g.set_axis_labels(etiqueta_x, etiqueta_y, fontsize=13, weight='semibold')
    g.figure.suptitle(titulo, y=1.02, fontsize=15, fontweight='bold')
    
    # Rotar etiquetas del eje x
    g.set_xticklabels(rotation=25, ha='right', fontsize=11)
    
    # Agregar etiquetas en las barras
    for ax in g.axes.flat:
        for container in ax.containers:
            labels = [f'{int(v.get_height())}' if v.get_height() > 0 else '' 
                     for v in container]
            ax.bar_label(container, labels=labels, padding=3, fontsize=10, weight='bold')
        
        # Líneas divisorias
        xticks = ax.get_xticks()
        for x in xticks[:-1]:
            ax.axvline(x + 0.5, color='lightgray', linestyle='--', linewidth=0.7, alpha=0.4)
        
        # Grid
        ax.grid(axis='y', alpha=0.25, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Ajustar límite Y
        ylim = ax.get_ylim()
        ax.set_ylim(ylim[0], ylim[1] * 1.08)
    
    # Preparar datos para la tabla (ordenados por total descendente)
    table_data_with_grupo = [
        (grupo, totales.get(grupo, 0), (totales.get(grupo, 0)/total_general*100))
        for grupo in orden_grupos
    ]
    table_data_with_grupo.sort(key=lambda x: x[2], reverse=True)
    
    # Preparar datos para la tabla
    if mostrar_porcentaje:
        table_data = [[count, f"{pct:.1f}%"] for grupo, count, pct in table_data_with_grupo]
        col_labels = ['Total', '%']
        col_widths = [0.25, 0.25]
    else:
        table_data = [[count] for grupo, count, pct in table_data_with_grupo]
        col_labels = ['Total']
        col_widths = [0.3]
    
    row_labels = [grupo for grupo, _, _ in table_data_with_grupo]
    
    # Determinar posición de la tabla
    posiciones = {
        'superior_derecha': [0.68, 0.55, 0.28, 0.35],
        'superior_izquierda': [0.05, 0.55, 0.28, 0.35],
        'inferior_derecha': [0.68, 0.05, 0.28, 0.35],
        'inferior_izquierda': [0.05, 0.05, 0.28, 0.35]
    }
    
    bbox_tabla = posiciones.get(posicion_tabla, posiciones['superior_derecha'])
    
    # Crear tabla
    table_ax = g.figure.add_axes(bbox_tabla)
    table_ax.axis('off')
    
    table_obj = table_ax.table(
        cellText=table_data,
        rowLabels=row_labels,
        colLabels=col_labels,
        cellLoc='center',
        rowLoc='left',
        loc='center',
        colWidths=col_widths
    )
    
    table_obj.auto_set_font_size(False)
    table_obj.set_fontsize(9)
    table_obj.scale(1, 1.5)
    
    # Estilizar tabla
    for i in range(len(col_labels)):
        table_obj[(0, i)].set_facecolor('#404040')
        table_obj[(0, i)].set_text_props(weight='bold', color='white', fontsize=10)
    
    for i, (grupo, _, _) in enumerate(table_data_with_grupo):
        table_obj[(i+1, -1)].set_facecolor(paleta_colores.get(grupo, '#808080'))
        table_obj[(i+1, -1)].set_text_props(weight='bold', color='white', ha='left', fontsize=8)
        
        for j in range(len(col_labels)):
            table_obj[(i+1, j)].set_facecolor('#F8F8F8')
            table_obj[(i+1, j)].set_text_props(weight='bold', fontsize=9)
    
    for key, cell in table_obj.get_celld().items():
        cell.set_edgecolor('#CCCCCC')
        cell.set_linewidth(1)
    
    plt.tight_layout()
    
    return g.figure