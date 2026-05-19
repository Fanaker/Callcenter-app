USE CallCenter;
GO

EXEC dbo.sp_listar_campanias_activas;
EXEC dbo.sp_listar_puestos_activos;
GO

EXEC dbo.sp_listar_requerimientos;
EXEC dbo.sp_obtener_requerimiento_por_codigo @codigo = 'RQ0001';
GO

EXEC dbo.sp_listar_postulaciones_por_requerimiento @codigo_requerimiento = 'RQ0001';
GO

EXEC dbo.sp_dashboard_general;
GO

EXEC dbo.sp_listar_formacion_por_requerimiento @codigo_requerimiento = 'RQ0001';
GO

DECLARE @idCampania INT = (SELECT TOP 1 id_campania FROM dbo.campanias WHERE activo = 1 ORDER BY id_campania);
DECLARE @idPuesto INT = (SELECT TOP 1 id_puesto FROM dbo.puestos WHERE activo = 1 ORDER BY id_puesto);

EXEC dbo.sp_crear_requerimiento
    @id_campania = @idCampania,
    @id_puesto = @idPuesto,
    @cantidad = 5,
    @dias_capacitacion = 6,
    @fecha_ingreso = '2026-07-10',
    @fecha_inicio_capacitacion = '2026-06-25',
    @fecha_fin_capacitacion = '2026-07-02',
    @comentarios = 'RQ de prueba generado desde procedimiento.',
    @creado_por_usuario_id = NULL;
GO
