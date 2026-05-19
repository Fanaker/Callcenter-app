/* =========================================================
   04_SEED_DATA
   Datos iniciales para demo académica.
   Ejecutar después de:
   01_create_database_and_tables.sql
   02_create_views.sql
   03_create_stored_procedures.sql
   ========================================================= */

USE CallCenter;
GO

/* =========================================================
   USUARIOS DEMO
   Nota:
   password_hash es demo. En producción se debe generar desde backend.
   ========================================================= */

IF NOT EXISTS (SELECT 1 FROM dbo.usuarios WHERE correo = 'admin@quantia.local')
BEGIN
    EXEC dbo.sp_crear_usuario
        @dni = '00000001',
        @nombre = 'María',
        @apellido = 'Torres',
        @correo = 'admin@quantia.local',
        @password_hash = '$demo_hash_admin',
        @rol = 'ADMIN';
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.usuarios WHERE correo = 'planeamiento@quantia.local')
BEGIN
    EXEC dbo.sp_crear_usuario
        @dni = '00000002',
        @nombre = 'Ana',
        @apellido = 'Rojas',
        @correo = 'planeamiento@quantia.local',
        @password_hash = '$demo_hash_planeamiento',
        @rol = 'PLANEAMIENTO';
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.usuarios WHERE correo = 'reclutamiento@quantia.local')
BEGIN
    EXEC dbo.sp_crear_usuario
        @dni = '00000003',
        @nombre = 'Luis',
        @apellido = 'Vega',
        @correo = 'reclutamiento@quantia.local',
        @password_hash = '$demo_hash_reclutamiento',
        @rol = 'RECLUTAMIENTO';
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.usuarios WHERE correo = 'formacion@quantia.local')
BEGIN
    EXEC dbo.sp_crear_usuario
        @dni = '00000004',
        @nombre = 'Carla',
        @apellido = 'Mendoza',
        @correo = 'formacion@quantia.local',
        @password_hash = '$demo_hash_formacion',
        @rol = 'FORMACION';
END;
GO


/* =========================================================
   CAMPAÑAS DEMO
   ========================================================= */

IF NOT EXISTS (SELECT 1 FROM dbo.campanias WHERE nombre = 'Renovación Proactiva')
BEGIN
    INSERT INTO dbo.campanias (nombre, codigo_centro_costo, activo)
    VALUES ('Renovación Proactiva', 'CC-RENOV-001', 1);
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.campanias WHERE nombre = 'Portabilidad Outbound')
BEGIN
    INSERT INTO dbo.campanias (nombre, codigo_centro_costo, activo)
    VALUES ('Portabilidad Outbound', 'CC-PORT-001', 1);
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.campanias WHERE nombre = 'Ventas Hogar')
BEGIN
    INSERT INTO dbo.campanias (nombre, codigo_centro_costo, activo)
    VALUES ('Ventas Hogar', 'CC-HOGAR-001', 1);
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.campanias WHERE nombre = 'Atención Empresas')
BEGIN
    INSERT INTO dbo.campanias (nombre, codigo_centro_costo, activo)
    VALUES ('Atención Empresas', 'CC-EMP-001', 1);
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.campanias WHERE nombre = 'Campaña Inactiva Demo')
BEGIN
    INSERT INTO dbo.campanias (nombre, codigo_centro_costo, activo)
    VALUES ('Campaña Inactiva Demo', 'CC-INACT-001', 0);
END;
GO


/* =========================================================
   PUESTOS DEMO
   ========================================================= */

IF NOT EXISTS (SELECT 1 FROM dbo.puestos WHERE nombre = 'Asesor de ventas')
BEGIN
    INSERT INTO dbo.puestos (nombre, descripcion, activo)
    VALUES ('Asesor de ventas', 'Atención comercial y cierre de ventas outbound.', 1);
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.puestos WHERE nombre = 'Asesor de atención al cliente')
BEGIN
    INSERT INTO dbo.puestos (nombre, descripcion, activo)
    VALUES ('Asesor de atención al cliente', 'Atención de consultas y soporte a clientes.', 1);
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.puestos WHERE nombre = 'Back Office Comercial')
BEGIN
    INSERT INTO dbo.puestos (nombre, descripcion, activo)
    VALUES ('Back Office Comercial', 'Gestión administrativa y validación de ventas.', 1);
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.puestos WHERE nombre = 'Supervisor Trainee')
BEGIN
    INSERT INTO dbo.puestos (nombre, descripcion, activo)
    VALUES ('Supervisor Trainee', 'Soporte operativo y seguimiento de asesores.', 0);
END;
GO


/* =========================================================
   REQUERIMIENTOS DEMO
   Casos cubiertos:
   - RQ0001: abierto, con postulantes en varios estados.
   - RQ0002: abierto, con postulantes para formación.
   - RQ0003: cerrado, sirve para probar bloqueo de postulación.
   - RQ0004: abierto, sin postulantes, sirve para empty states.
   - RQ0005: abierto, otra campaña y otro puesto.
   ========================================================= */

DECLARE @campaniaRenovacion INT = (SELECT id_campania FROM dbo.campanias WHERE nombre = 'Renovación Proactiva');
DECLARE @campaniaPortabilidad INT = (SELECT id_campania FROM dbo.campanias WHERE nombre = 'Portabilidad Outbound');
DECLARE @campaniaHogar INT = (SELECT id_campania FROM dbo.campanias WHERE nombre = 'Ventas Hogar');
DECLARE @campaniaEmpresas INT = (SELECT id_campania FROM dbo.campanias WHERE nombre = 'Atención Empresas');

DECLARE @puestoVentas INT = (SELECT id_puesto FROM dbo.puestos WHERE nombre = 'Asesor de ventas');
DECLARE @puestoAtencion INT = (SELECT id_puesto FROM dbo.puestos WHERE nombre = 'Asesor de atención al cliente');
DECLARE @puestoBackOffice INT = (SELECT id_puesto FROM dbo.puestos WHERE nombre = 'Back Office Comercial');

IF NOT EXISTS (SELECT 1 FROM dbo.requerimientos WHERE codigo = 'RQ0001')
BEGIN
    INSERT INTO dbo.requerimientos (
        codigo,
        id_campania,
        id_puesto,
        cantidad,
        dias_capacitacion,
        fecha_ingreso,
        fecha_inicio_capacitacion,
        fecha_fin_capacitacion,
        comentarios,
        estado
    )
    VALUES (
        'RQ0001',
        @campaniaRenovacion,
        @puestoVentas,
        10,
        7,
        '2026-06-10',
        '2026-05-28',
        '2026-06-04',
        'Requerimiento inicial para campaña comercial outbound.',
        'ABIERTO'
    );

    INSERT INTO dbo.configuracion_formacion (id_requerimiento, test_count, aprobacion_promedio)
    VALUES (SCOPE_IDENTITY(), 3, 14.00);
END;

IF NOT EXISTS (SELECT 1 FROM dbo.requerimientos WHERE codigo = 'RQ0002')
BEGIN
    INSERT INTO dbo.requerimientos (
        codigo,
        id_campania,
        id_puesto,
        cantidad,
        dias_capacitacion,
        fecha_ingreso,
        fecha_inicio_capacitacion,
        fecha_fin_capacitacion,
        comentarios,
        estado
    )
    VALUES (
        'RQ0002',
        @campaniaPortabilidad,
        @puestoVentas,
        15,
        8,
        '2026-06-17',
        '2026-06-01',
        '2026-06-09',
        'Refuerzo de dotación para nueva base de clientes.',
        'ABIERTO'
    );

    INSERT INTO dbo.configuracion_formacion (id_requerimiento, test_count, aprobacion_promedio)
    VALUES (SCOPE_IDENTITY(), 4, 13.50);
END;

IF NOT EXISTS (SELECT 1 FROM dbo.requerimientos WHERE codigo = 'RQ0003')
BEGIN
    INSERT INTO dbo.requerimientos (
        codigo,
        id_campania,
        id_puesto,
        cantidad,
        dias_capacitacion,
        fecha_ingreso,
        fecha_inicio_capacitacion,
        fecha_fin_capacitacion,
        comentarios,
        estado
    )
    VALUES (
        'RQ0003',
        @campaniaHogar,
        @puestoAtencion,
        8,
        6,
        '2026-06-24',
        '2026-06-10',
        '2026-06-17',
        'Requerimiento cerrado para probar bloqueo de postulaciones.',
        'ABIERTO'
    );

    INSERT INTO dbo.configuracion_formacion (id_requerimiento, test_count, aprobacion_promedio)
    VALUES (SCOPE_IDENTITY(), 3, 14.00);
END;

IF NOT EXISTS (SELECT 1 FROM dbo.requerimientos WHERE codigo = 'RQ0004')
BEGIN
    INSERT INTO dbo.requerimientos (
        codigo,
        id_campania,
        id_puesto,
        cantidad,
        dias_capacitacion,
        fecha_ingreso,
        fecha_inicio_capacitacion,
        fecha_fin_capacitacion,
        comentarios,
        estado
    )
    VALUES (
        'RQ0004',
        @campaniaEmpresas,
        @puestoBackOffice,
        5,
        5,
        '2026-07-01',
        '2026-06-18',
        '2026-06-25',
        'RQ abierto sin postulantes para probar estados vacíos.',
        'ABIERTO'
    );

    INSERT INTO dbo.configuracion_formacion (id_requerimiento, test_count, aprobacion_promedio)
    VALUES (SCOPE_IDENTITY(), 2, 15.00);
END;

IF NOT EXISTS (SELECT 1 FROM dbo.requerimientos WHERE codigo = 'RQ0005')
BEGIN
    INSERT INTO dbo.requerimientos (
        codigo,
        id_campania,
        id_puesto,
        cantidad,
        dias_capacitacion,
        fecha_ingreso,
        fecha_inicio_capacitacion,
        fecha_fin_capacitacion,
        comentarios,
        estado
    )
    VALUES (
        'RQ0005',
        @campaniaHogar,
        @puestoVentas,
        12,
        7,
        '2026-07-08',
        '2026-06-24',
        '2026-07-01',
        'Requerimiento de ventas hogar para probar filtros por campaña.',
        'ABIERTO'
    );

    INSERT INTO dbo.configuracion_formacion (id_requerimiento, test_count, aprobacion_promedio)
    VALUES (SCOPE_IDENTITY(), 3, 14.00);
END;
GO


/* =========================================================
   POSTULANTES Y POSTULACIONES
   RQ0001: mezcla de estados para probar Reclutamiento y Formación.
   ========================================================= */

IF NOT EXISTS (
    SELECT 1
    FROM dbo.vw_postulaciones_frontend
    WHERE rqCodigo = 'RQ0001'
      AND dni = '74125896'
)
BEGIN
    EXEC dbo.sp_registrar_postulacion
        @codigo_requerimiento = 'RQ0001',
        @dni = '74125896',
        @nombre = 'Ana',
        @apellido = 'Gómez',
        @correo = 'ana.gomez@example.com',
        @telefono = '987654321',
        @medio_preferido = 'whatsapp',
        @cv_url = 'https://drive.google.com/file/d/demo-ana/view',
        @comentarios = 'Disponibilidad inmediata.';
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM dbo.vw_postulaciones_frontend
    WHERE rqCodigo = 'RQ0001'
      AND dni = '85236974'
)
BEGIN
    EXEC dbo.sp_registrar_postulacion
        @codigo_requerimiento = 'RQ0001',
        @dni = '85236974',
        @nombre = 'Bruno',
        @apellido = 'Salazar',
        @correo = 'bruno.salazar@example.com',
        @telefono = '912345678',
        @medio_preferido = 'llamada',
        @cv_url = 'https://drive.google.com/file/d/demo-bruno/view',
        @comentarios = 'Experiencia previa en ventas.';
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM dbo.vw_postulaciones_frontend
    WHERE rqCodigo = 'RQ0001'
      AND dni = '96385274'
)
BEGIN
    EXEC dbo.sp_registrar_postulacion
        @codigo_requerimiento = 'RQ0001',
        @dni = '96385274',
        @nombre = 'Carla',
        @apellido = 'Pérez',
        @correo = 'carla.perez@example.com',
        @telefono = '923456789',
        @medio_preferido = 'email',
        @cv_url = 'https://drive.google.com/file/d/demo-carla/view',
        @comentarios = 'Puede iniciar en horario tarde.';
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM dbo.vw_postulaciones_frontend
    WHERE rqCodigo = 'RQ0001'
      AND dni = '15975346'
)
BEGIN
    EXEC dbo.sp_registrar_postulacion
        @codigo_requerimiento = 'RQ0001',
        @dni = '15975346',
        @nombre = 'Diego',
        @apellido = 'López',
        @correo = 'diego.lopez@example.com',
        @telefono = '934567890',
        @medio_preferido = 'whatsapp',
        @cv_url = 'https://drive.google.com/file/d/demo-diego/view',
        @comentarios = 'Sin experiencia comercial.';
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM dbo.vw_postulaciones_frontend
    WHERE rqCodigo = 'RQ0001'
      AND dni = '35715984'
)
BEGIN
    EXEC dbo.sp_registrar_postulacion
        @codigo_requerimiento = 'RQ0001',
        @dni = '35715984',
        @nombre = 'Elena',
        @apellido = 'Ramírez',
        @correo = 'elena.ramirez@example.com',
        @telefono = '945678901',
        @medio_preferido = 'whatsapp',
        @cv_url = 'https://drive.google.com/file/d/demo-elena/view',
        @comentarios = 'Postulación recién registrada.';
END;
GO


/* =========================================================
   AVANCE RECLUTAMIENTO RQ0001
   Ana: apta + entrevista aprobada + contratada + formación aprobada.
   Bruno: apto + entrevista aprobada + formación desaprobada.
   Carla: apta, pero entrevista no aprobada.
   Diego: no apto.
   Elena: sin evaluar.
   ========================================================= */

DECLARE @idAna INT = (
    SELECT idPostulacion
    FROM dbo.vw_postulaciones_frontend
    WHERE rqCodigo = 'RQ0001'
      AND dni = '74125896'
);

IF @idAna IS NOT NULL
BEGIN
    EXEC dbo.sp_actualizar_requisito_postulacion @id_postulacion = @idAna, @apto = 1;
    EXEC dbo.sp_actualizar_entrevista_postulacion @id_postulacion = @idAna, @entrevista_aprobada = 1;
    EXEC dbo.sp_actualizar_contratacion_postulacion @id_postulacion = @idAna, @contratar = 1;
    EXEC dbo.sp_guardar_nota_formacion @id_postulacion = @idAna, @nro_evaluacion = 1, @nota = 15;
    EXEC dbo.sp_guardar_nota_formacion @id_postulacion = @idAna, @nro_evaluacion = 2, @nota = 16;
    EXEC dbo.sp_guardar_nota_formacion @id_postulacion = @idAna, @nro_evaluacion = 3, @nota = 14;
END;
GO

DECLARE @idBruno INT = (
    SELECT idPostulacion
    FROM dbo.vw_postulaciones_frontend
    WHERE rqCodigo = 'RQ0001'
      AND dni = '85236974'
);

IF @idBruno IS NOT NULL
BEGIN
    EXEC dbo.sp_actualizar_requisito_postulacion @id_postulacion = @idBruno, @apto = 1;
    EXEC dbo.sp_actualizar_entrevista_postulacion @id_postulacion = @idBruno, @entrevista_aprobada = 1;
    EXEC dbo.sp_actualizar_contratacion_postulacion @id_postulacion = @idBruno, @contratar = 0;
    EXEC dbo.sp_guardar_nota_formacion @id_postulacion = @idBruno, @nro_evaluacion = 1, @nota = 11;
    EXEC dbo.sp_guardar_nota_formacion @id_postulacion = @idBruno, @nro_evaluacion = 2, @nota = 12;
    EXEC dbo.sp_guardar_nota_formacion @id_postulacion = @idBruno, @nro_evaluacion = 3, @nota = 10;
END;
GO

DECLARE @idCarla INT = (
    SELECT idPostulacion
    FROM dbo.vw_postulaciones_frontend
    WHERE rqCodigo = 'RQ0001'
      AND dni = '96385274'
);

IF @idCarla IS NOT NULL
BEGIN
    EXEC dbo.sp_actualizar_requisito_postulacion @id_postulacion = @idCarla, @apto = 1;
    EXEC dbo.sp_actualizar_entrevista_postulacion @id_postulacion = @idCarla, @entrevista_aprobada = 0;
END;
GO

DECLARE @idDiego INT = (
    SELECT idPostulacion
    FROM dbo.vw_postulaciones_frontend
    WHERE rqCodigo = 'RQ0001'
      AND dni = '15975346'
);

IF @idDiego IS NOT NULL
BEGIN
    EXEC dbo.sp_actualizar_requisito_postulacion @id_postulacion = @idDiego, @apto = 0;
END;
GO


/* =========================================================
   RQ0002: postulantes para probar otra configuración de formación.
   ========================================================= */

IF NOT EXISTS (
    SELECT 1
    FROM dbo.vw_postulaciones_frontend
    WHERE rqCodigo = 'RQ0002'
      AND dni = '75395128'
)
BEGIN
    EXEC dbo.sp_registrar_postulacion
        @codigo_requerimiento = 'RQ0002',
        @dni = '75395128',
        @nombre = 'Fernando',
        @apellido = 'Castillo',
        @correo = 'fernando.castillo@example.com',
        @telefono = '956789012',
        @medio_preferido = 'llamada',
        @cv_url = 'https://drive.google.com/file/d/demo-fernando/view',
        @comentarios = 'Experiencia en call center.';
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM dbo.vw_postulaciones_frontend
    WHERE rqCodigo = 'RQ0002'
      AND dni = '95175328'
)
BEGIN
    EXEC dbo.sp_registrar_postulacion
        @codigo_requerimiento = 'RQ0002',
        @dni = '95175328',
        @nombre = 'Gabriela',
        @apellido = 'Flores',
        @correo = 'gabriela.flores@example.com',
        @telefono = '967890123',
        @medio_preferido = 'whatsapp',
        @cv_url = 'https://drive.google.com/file/d/demo-gabriela/view',
        @comentarios = 'Buena disponibilidad horaria.';
END;
GO

DECLARE @idFernando INT = (
    SELECT idPostulacion
    FROM dbo.vw_postulaciones_frontend
    WHERE rqCodigo = 'RQ0002'
      AND dni = '75395128'
);

IF @idFernando IS NOT NULL
BEGIN
    EXEC dbo.sp_actualizar_requisito_postulacion @id_postulacion = @idFernando, @apto = 1;
    EXEC dbo.sp_actualizar_entrevista_postulacion @id_postulacion = @idFernando, @entrevista_aprobada = 1;
    EXEC dbo.sp_guardar_nota_formacion @id_postulacion = @idFernando, @nro_evaluacion = 1, @nota = 13;
    EXEC dbo.sp_guardar_nota_formacion @id_postulacion = @idFernando, @nro_evaluacion = 2, @nota = 14;
    EXEC dbo.sp_guardar_nota_formacion @id_postulacion = @idFernando, @nro_evaluacion = 3, @nota = 15;
    EXEC dbo.sp_guardar_nota_formacion @id_postulacion = @idFernando, @nro_evaluacion = 4, @nota = 14;
END;
GO

DECLARE @idGabriela INT = (
    SELECT idPostulacion
    FROM dbo.vw_postulaciones_frontend
    WHERE rqCodigo = 'RQ0002'
      AND dni = '95175328'
);

IF @idGabriela IS NOT NULL
BEGIN
    EXEC dbo.sp_actualizar_requisito_postulacion @id_postulacion = @idGabriela, @apto = 1;
    EXEC dbo.sp_actualizar_entrevista_postulacion @id_postulacion = @idGabriela, @entrevista_aprobada = 1;
    EXEC dbo.sp_guardar_nota_formacion @id_postulacion = @idGabriela, @nro_evaluacion = 1, @nota = 18;
    EXEC dbo.sp_guardar_nota_formacion @id_postulacion = @idGabriela, @nro_evaluacion = 2, @nota = 17;
    EXEC dbo.sp_guardar_nota_formacion @id_postulacion = @idGabriela, @nro_evaluacion = 3, @nota = 16;
    EXEC dbo.sp_guardar_nota_formacion @id_postulacion = @idGabriela, @nro_evaluacion = 4, @nota = 18;
END;
GO


/* =========================================================
   RQ0003: candidato registrado y luego RQ cerrado.
   Sirve para probar pantalla pública bloqueada.
   ========================================================= */

IF NOT EXISTS (
    SELECT 1
    FROM dbo.vw_postulaciones_frontend
    WHERE rqCodigo = 'RQ0003'
      AND dni = '14725836'
)
BEGIN
    EXEC dbo.sp_registrar_postulacion
        @codigo_requerimiento = 'RQ0003',
        @dni = '14725836',
        @nombre = 'Hugo',
        @apellido = 'Navarro',
        @correo = 'hugo.navarro@example.com',
        @telefono = '978901234',
        @medio_preferido = 'email',
        @cv_url = 'https://drive.google.com/file/d/demo-hugo/view',
        @comentarios = 'Postulación de RQ que será cerrado.';
END;
GO

UPDATE dbo.requerimientos
SET estado = 'CERRADO',
    updated_at = SYSDATETIME()
WHERE codigo = 'RQ0003';
GO


/* =========================================================
   RQ0005: otro caso para filtros por campaña y postulantes.
   ========================================================= */

IF NOT EXISTS (
    SELECT 1
    FROM dbo.vw_postulaciones_frontend
    WHERE rqCodigo = 'RQ0005'
      AND dni = '36925814'
)
BEGIN
    EXEC dbo.sp_registrar_postulacion
        @codigo_requerimiento = 'RQ0005',
        @dni = '36925814',
        @nombre = 'Ivana',
        @apellido = 'Soto',
        @correo = 'ivana.soto@example.com',
        @telefono = '989012345',
        @medio_preferido = 'whatsapp',
        @cv_url = 'https://drive.google.com/file/d/demo-ivana/view',
        @comentarios = 'Interesada en ventas hogar.';
END;
GO

DECLARE @idIvana INT = (
    SELECT idPostulacion
    FROM dbo.vw_postulaciones_frontend
    WHERE rqCodigo = 'RQ0005'
      AND dni = '36925814'
);

IF @idIvana IS NOT NULL
BEGIN
    EXEC dbo.sp_actualizar_requisito_postulacion @id_postulacion = @idIvana, @apto = 1;
END;
GO


/* =========================================================
   REINICIAR SEQUENCE PARA EVITAR CHOQUES CON RQ0001-RQ0005
   Los nuevos RQ creados por procedimiento empezarán desde RQ0100.
   ========================================================= */

ALTER SEQUENCE dbo.seq_requerimiento_codigo RESTART WITH 100;
GO


/* =========================================================
   VALIDACIÓN FINAL DEL SEED
   ========================================================= */

SELECT 'Campañas activas' AS validacion, COUNT(*) AS total
FROM dbo.campanias
WHERE activo = 1;

SELECT 'Puestos activos' AS validacion, COUNT(*) AS total
FROM dbo.puestos
WHERE activo = 1;

SELECT 'Requerimientos' AS validacion, COUNT(*) AS total
FROM dbo.requerimientos;

SELECT 'Postulaciones' AS validacion, COUNT(*) AS total
FROM dbo.postulaciones;

SELECT 'Evaluaciones formación' AS validacion, COUNT(*) AS total
FROM dbo.evaluaciones_formacion;
GO