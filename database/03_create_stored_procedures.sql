USE CallCenter;
GO

CREATE OR ALTER PROCEDURE dbo.sp_crear_usuario
    @dni CHAR(8), @nombre VARCHAR(80), @apellido VARCHAR(80),
    @correo VARCHAR(120), @password_hash VARCHAR(255), @rol VARCHAR(30)
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO dbo.usuarios (dni, nombre, apellido, correo, password_hash, rol)
    VALUES (@dni, @nombre, @apellido, @correo, @password_hash, @rol);
    SELECT id_usuario AS idUsuario, dni, nombre, apellido, correo, rol, activo
    FROM dbo.usuarios WHERE id_usuario = SCOPE_IDENTITY();
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_obtener_usuario_por_correo
    @correo VARCHAR(120)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT id_usuario AS idUsuario, dni, nombre, apellido, correo,
           password_hash AS passwordHash, rol, activo
    FROM dbo.usuarios
    WHERE correo = @correo AND activo = 1;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_listar_campanias_activas
AS
BEGIN
    SET NOCOUNT ON;
    SELECT id_campania AS id, nombre, codigo_centro_costo AS codigoCentroCosto,
           CASE WHEN activo = 1 THEN 'ACTIVA' ELSE 'INACTIVA' END AS estado
    FROM dbo.campanias
    WHERE activo = 1
    ORDER BY nombre;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_listar_puestos_activos
AS
BEGIN
    SET NOCOUNT ON;
    SELECT id_puesto AS id, nombre, descripcion,
           CASE WHEN activo = 1 THEN 'ACTIVO' ELSE 'INACTIVO' END AS estado
    FROM dbo.puestos
    WHERE activo = 1
    ORDER BY nombre;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_listar_requerimientos
    @estado VARCHAR(20) = NULL,
    @id_campania INT = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SELECT *
    FROM dbo.vw_requerimientos_frontend
    WHERE (@estado IS NULL OR estado = @estado)
      AND (@id_campania IS NULL OR campaniaId = @id_campania)
    ORDER BY idRequerimiento DESC;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_obtener_requerimiento_por_codigo
    @codigo VARCHAR(30)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM dbo.vw_requerimientos_frontend WHERE codigo = @codigo;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_crear_requerimiento
    @id_campania INT,
    @id_puesto INT,
    @cantidad INT,
    @dias_capacitacion INT,
    @fecha_ingreso DATE,
    @fecha_inicio_capacitacion DATE,
    @fecha_fin_capacitacion DATE,
    @comentarios VARCHAR(255) = NULL,
    @creado_por_usuario_id INT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    IF NOT EXISTS (SELECT 1 FROM dbo.campanias WHERE id_campania = @id_campania AND activo = 1)
        THROW 51001, 'La campaña no existe o no está activa.', 1;
    IF NOT EXISTS (SELECT 1 FROM dbo.puestos WHERE id_puesto = @id_puesto AND activo = 1)
        THROW 51002, 'El puesto no existe o no está activo.', 1;
    IF @cantidad <= 0 THROW 51003, 'La cantidad debe ser mayor a cero.', 1;
    IF @dias_capacitacion <= 0 THROW 51004, 'Los días de capacitación deben ser mayores a cero.', 1;
    IF @fecha_fin_capacitacion >= @fecha_ingreso
        THROW 51005, 'La fecha fin de capacitación debe ser anterior a la fecha de ingreso.', 1;
    IF DATEDIFF(DAY, @fecha_inicio_capacitacion, @fecha_fin_capacitacion) < 3
        THROW 51006, 'La capacitación debe tener al menos 3 días entre inicio y fin.', 1;

    DECLARE @numero INT = NEXT VALUE FOR dbo.seq_requerimiento_codigo;
    DECLARE @codigo VARCHAR(30) = CONCAT('RQ', RIGHT(CONCAT('0000', @numero), 4));

    INSERT INTO dbo.requerimientos (
        codigo, id_campania, id_puesto, cantidad, dias_capacitacion,
        fecha_ingreso, fecha_inicio_capacitacion, fecha_fin_capacitacion,
        comentarios, estado, creado_por_usuario_id
    )
    VALUES (
        @codigo, @id_campania, @id_puesto, @cantidad, @dias_capacitacion,
        @fecha_ingreso, @fecha_inicio_capacitacion, @fecha_fin_capacitacion,
        @comentarios, 'ABIERTO', @creado_por_usuario_id
    );

    DECLARE @id_requerimiento INT = SCOPE_IDENTITY();
    INSERT INTO dbo.configuracion_formacion (id_requerimiento, test_count, aprobacion_promedio)
    VALUES (@id_requerimiento, 3, 14.00);

    SELECT * FROM dbo.vw_requerimientos_frontend WHERE idRequerimiento = @id_requerimiento;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_actualizar_estado_requerimiento
    @codigo VARCHAR(30), @estado VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    IF @estado NOT IN ('ABIERTO','CERRADO')
        THROW 51007, 'Estado inválido. Use ABIERTO o CERRADO.', 1;
    UPDATE dbo.requerimientos SET estado = @estado, updated_at = SYSDATETIME()
    WHERE codigo = @codigo;
    IF @@ROWCOUNT = 0 THROW 51008, 'Requerimiento no encontrado.', 1;
    SELECT * FROM dbo.vw_requerimientos_frontend WHERE codigo = @codigo;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_registrar_postulacion
    @codigo_requerimiento VARCHAR(30), @dni CHAR(8), @nombre VARCHAR(80),
    @apellido VARCHAR(80), @correo VARCHAR(120), @telefono VARCHAR(15),
    @medio_preferido VARCHAR(20), @cv_url VARCHAR(500), @comentarios VARCHAR(500) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @id_requerimiento INT, @id_postulante INT;

    SELECT @id_requerimiento = id_requerimiento
    FROM dbo.requerimientos
    WHERE codigo = @codigo_requerimiento AND estado = 'ABIERTO';
    IF @id_requerimiento IS NULL THROW 52001, 'Requerimiento no encontrado o cerrado.', 1;
    IF @medio_preferido NOT IN ('whatsapp','llamada','email') THROW 52002, 'Medio preferido inválido.', 1;
    IF @cv_url NOT LIKE 'https://%' THROW 52003, 'El enlace del CV debe iniciar con https://.', 1;

    SELECT @id_postulante = id_postulante FROM dbo.postulantes WHERE dni = @dni;

    IF @id_postulante IS NULL
    BEGIN
        INSERT INTO dbo.postulantes (dni, nombre, apellido, correo, telefono, medio_preferido)
        VALUES (@dni, @nombre, @apellido, @correo, @telefono, @medio_preferido);
        SET @id_postulante = SCOPE_IDENTITY();
    END
    ELSE
    BEGIN
        UPDATE dbo.postulantes
        SET nombre = @nombre, apellido = @apellido, correo = @correo,
            telefono = @telefono, medio_preferido = @medio_preferido,
            updated_at = SYSDATETIME()
        WHERE id_postulante = @id_postulante;
    END;

    IF EXISTS (SELECT 1 FROM dbo.postulaciones WHERE id_requerimiento = @id_requerimiento AND id_postulante = @id_postulante)
        THROW 52004, 'El postulante ya se encuentra registrado en este requerimiento.', 1;

    INSERT INTO dbo.postulaciones (id_requerimiento, id_postulante, cv_url, comentarios, apto, entrevista_aprobada, contratar)
    VALUES (@id_requerimiento, @id_postulante, @cv_url, @comentarios, 0, 0, 0);

    SELECT * FROM dbo.vw_postulaciones_frontend WHERE idPostulacion = SCOPE_IDENTITY();
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_listar_postulaciones_por_requerimiento
    @codigo_requerimiento VARCHAR(30)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM dbo.vw_postulaciones_frontend
    WHERE rqCodigo = @codigo_requerimiento
    ORDER BY fechaPostulacion DESC;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_actualizar_requisito_postulacion
    @id_postulacion INT, @apto BIT
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE dbo.postulaciones
    SET apto = @apto,
        entrevista_aprobada = CASE WHEN @apto = 0 THEN 0 ELSE entrevista_aprobada END,
        contratar = CASE WHEN @apto = 0 THEN 0 ELSE contratar END,
        fecha_contratacion = CASE WHEN @apto = 0 THEN NULL ELSE fecha_contratacion END,
        updated_at = SYSDATETIME()
    WHERE id_postulacion = @id_postulacion;
    IF @@ROWCOUNT = 0 THROW 52005, 'Postulación no encontrada.', 1;
    SELECT * FROM dbo.vw_postulaciones_frontend WHERE idPostulacion = @id_postulacion;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_actualizar_entrevista_postulacion
    @id_postulacion INT, @entrevista_aprobada BIT
AS
BEGIN
    SET NOCOUNT ON;
    IF @entrevista_aprobada = 1 AND NOT EXISTS (SELECT 1 FROM dbo.postulaciones WHERE id_postulacion = @id_postulacion AND apto = 1)
        THROW 52006, 'No se puede aprobar entrevista si el postulante no cumple requisito.', 1;
    UPDATE dbo.postulaciones
    SET entrevista_aprobada = @entrevista_aprobada,
        contratar = CASE WHEN @entrevista_aprobada = 0 THEN 0 ELSE contratar END,
        fecha_contratacion = CASE WHEN @entrevista_aprobada = 0 THEN NULL ELSE fecha_contratacion END,
        updated_at = SYSDATETIME()
    WHERE id_postulacion = @id_postulacion;
    IF @@ROWCOUNT = 0 THROW 52007, 'Postulación no encontrada.', 1;
    SELECT * FROM dbo.vw_postulaciones_frontend WHERE idPostulacion = @id_postulacion;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_actualizar_contratacion_postulacion
    @id_postulacion INT, @contratar BIT
AS
BEGIN
    SET NOCOUNT ON;
    IF @contratar = 1 AND NOT EXISTS (SELECT 1 FROM dbo.postulaciones WHERE id_postulacion = @id_postulacion AND apto = 1 AND entrevista_aprobada = 1)
        THROW 52008, 'Solo se puede contratar a postulantes aptos con entrevista aprobada.', 1;
    UPDATE dbo.postulaciones
    SET contratar = @contratar,
        fecha_contratacion = CASE WHEN @contratar = 1 THEN SYSDATETIME() ELSE NULL END,
        updated_at = SYSDATETIME()
    WHERE id_postulacion = @id_postulacion;
    IF @@ROWCOUNT = 0 THROW 52009, 'Postulación no encontrada.', 1;
    SELECT * FROM dbo.vw_postulaciones_frontend WHERE idPostulacion = @id_postulacion;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_configurar_formacion
    @codigo_requerimiento VARCHAR(30), @test_count INT, @aprobacion_promedio DECIMAL(5,2)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @id_requerimiento INT;
    SELECT @id_requerimiento = id_requerimiento FROM dbo.requerimientos WHERE codigo = @codigo_requerimiento;
    IF @id_requerimiento IS NULL THROW 53001, 'Requerimiento no encontrado.', 1;
    IF @test_count NOT BETWEEN 1 AND 5 THROW 53002, 'La cantidad de evaluaciones debe estar entre 1 y 5.', 1;
    IF @aprobacion_promedio NOT BETWEEN 0 AND 20 THROW 53003, 'La nota aprobatoria debe estar entre 0 y 20.', 1;

    IF EXISTS (SELECT 1 FROM dbo.configuracion_formacion WHERE id_requerimiento = @id_requerimiento)
        UPDATE dbo.configuracion_formacion
        SET test_count = @test_count, aprobacion_promedio = @aprobacion_promedio, updated_at = SYSDATETIME()
        WHERE id_requerimiento = @id_requerimiento;
    ELSE
        INSERT INTO dbo.configuracion_formacion (id_requerimiento, test_count, aprobacion_promedio)
        VALUES (@id_requerimiento, @test_count, @aprobacion_promedio);

    SELECT * FROM dbo.vw_requerimientos_frontend WHERE codigo = @codigo_requerimiento;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_guardar_nota_formacion
    @id_postulacion INT, @nro_evaluacion INT, @nota DECIMAL(5,2)
AS
BEGIN
    SET NOCOUNT ON;
    IF @nro_evaluacion NOT BETWEEN 1 AND 5 THROW 53004, 'El número de evaluación debe estar entre 1 y 5.', 1;
    IF @nota NOT BETWEEN 0 AND 20 THROW 53005, 'La nota debe estar entre 0 y 20.', 1;
    IF NOT EXISTS (SELECT 1 FROM dbo.postulaciones WHERE id_postulacion = @id_postulacion AND apto = 1 AND entrevista_aprobada = 1)
        THROW 53006, 'Solo se registran notas para postulantes aptos y con entrevista aprobada.', 1;

    IF EXISTS (SELECT 1 FROM dbo.evaluaciones_formacion WHERE id_postulacion = @id_postulacion AND nro_evaluacion = @nro_evaluacion)
        UPDATE dbo.evaluaciones_formacion SET nota = @nota, updated_at = SYSDATETIME()
        WHERE id_postulacion = @id_postulacion AND nro_evaluacion = @nro_evaluacion;
    ELSE
        INSERT INTO dbo.evaluaciones_formacion (id_postulacion, nro_evaluacion, nota)
        VALUES (@id_postulacion, @nro_evaluacion, @nota);

    SELECT * FROM dbo.vw_postulaciones_frontend WHERE idPostulacion = @id_postulacion;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_listar_formacion_por_requerimiento
    @codigo_requerimiento VARCHAR(30)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @test_count INT, @aprobacion_promedio DECIMAL(5,2);
    SELECT @test_count = testCount, @aprobacion_promedio = aprobacionPromedio
    FROM dbo.vw_requerimientos_frontend WHERE codigo = @codigo_requerimiento;

    SELECT
        p.*,
        CAST((
            CASE WHEN @test_count >= 1 THEN p.test1 ELSE 0 END +
            CASE WHEN @test_count >= 2 THEN p.test2 ELSE 0 END +
            CASE WHEN @test_count >= 3 THEN p.test3 ELSE 0 END +
            CASE WHEN @test_count >= 4 THEN p.test4 ELSE 0 END +
            CASE WHEN @test_count >= 5 THEN p.test5 ELSE 0 END
        ) / NULLIF(@test_count, 0) AS DECIMAL(5,2)) AS promedio,
        CAST(CASE WHEN (
            CASE WHEN @test_count >= 1 THEN p.test1 ELSE 0 END +
            CASE WHEN @test_count >= 2 THEN p.test2 ELSE 0 END +
            CASE WHEN @test_count >= 3 THEN p.test3 ELSE 0 END +
            CASE WHEN @test_count >= 4 THEN p.test4 ELSE 0 END +
            CASE WHEN @test_count >= 5 THEN p.test5 ELSE 0 END
        ) / NULLIF(@test_count, 0) >= @aprobacion_promedio THEN 1 ELSE 0 END AS BIT) AS formacionAprobada
    FROM dbo.vw_postulaciones_frontend p
    WHERE p.rqCodigo = @codigo_requerimiento AND p.apto = 1 AND p.entrevistaAprobada = 1
    ORDER BY p.apellido, p.nombre;
END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_dashboard_general
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        (SELECT COUNT(*) FROM dbo.requerimientos) AS totalRqs,
        (SELECT COUNT(*) FROM dbo.requerimientos WHERE estado = 'ABIERTO') AS activeRqs,
        (SELECT ISNULL(SUM(cantidad), 0) FROM dbo.requerimientos WHERE estado = 'ABIERTO') AS totalPersonalRequerido,
        (SELECT COUNT(DISTINCT id_postulante) FROM dbo.postulaciones) AS totalPostulantes,
        (SELECT COUNT(*) FROM dbo.postulaciones WHERE contratar = 1) AS contratados;
END;
GO
