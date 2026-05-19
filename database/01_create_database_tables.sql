CREATE DATABASE CallCenter;
END;
GO

USE CallCenter;
GO

ALTER DATABASE CallCenter SET READ_COMMITTED_SNAPSHOT ON WITH ROLLBACK IMMEDIATE;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.sequences
    WHERE name = 'seq_requerimiento_codigo'
      AND SCHEMA_NAME(schema_id) = 'dbo'
)
BEGIN
    CREATE SEQUENCE dbo.seq_requerimiento_codigo
        AS INT
        START WITH 1
        INCREMENT BY 1;
END;
GO

IF OBJECT_ID('dbo.usuarios', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.usuarios (
        id_usuario INT IDENTITY(1,1) NOT NULL,
        dni CHAR(8) NOT NULL,
        nombre VARCHAR(80) NOT NULL,
        apellido VARCHAR(80) NOT NULL,
        correo VARCHAR(120) NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        rol VARCHAR(30) NOT NULL,
        activo BIT NOT NULL CONSTRAINT df_usuarios_activo DEFAULT 1,
        created_at DATETIME2(0) NOT NULL CONSTRAINT df_usuarios_created_at DEFAULT SYSDATETIME(),
        updated_at DATETIME2(0) NULL,
        CONSTRAINT pk_usuarios PRIMARY KEY (id_usuario),
        CONSTRAINT uq_usuarios_dni UNIQUE (dni),
        CONSTRAINT uq_usuarios_correo UNIQUE (correo),
        CONSTRAINT chk_usuarios_dni CHECK (dni NOT LIKE '%[^0-9]%' AND LEN(dni) = 8),
        CONSTRAINT chk_usuarios_rol CHECK (rol IN ('ADMIN','PLANEAMIENTO','RECLUTAMIENTO','FORMACION','JEFE'))
    );
END;
GO

IF OBJECT_ID('dbo.campanias', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.campanias (
        id_campania INT IDENTITY(1,1) NOT NULL,
        nombre VARCHAR(100) NOT NULL,
        codigo_centro_costo VARCHAR(30) NULL,
        activo BIT NOT NULL CONSTRAINT df_campanias_activo DEFAULT 1,
        created_at DATETIME2(0) NOT NULL CONSTRAINT df_campanias_created_at DEFAULT SYSDATETIME(),
        updated_at DATETIME2(0) NULL,
        CONSTRAINT pk_campanias PRIMARY KEY (id_campania),
        CONSTRAINT uq_campanias_nombre UNIQUE (nombre),
        CONSTRAINT uq_campanias_codigo_centro_costo UNIQUE (codigo_centro_costo)
    );
END;
GO

IF OBJECT_ID('dbo.puestos', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.puestos (
        id_puesto INT IDENTITY(1,1) NOT NULL,
        nombre VARCHAR(100) NOT NULL,
        descripcion VARCHAR(255) NULL,
        activo BIT NOT NULL CONSTRAINT df_puestos_activo DEFAULT 1,
        created_at DATETIME2(0) NOT NULL CONSTRAINT df_puestos_created_at DEFAULT SYSDATETIME(),
        updated_at DATETIME2(0) NULL,
        CONSTRAINT pk_puestos PRIMARY KEY (id_puesto),
        CONSTRAINT uq_puestos_nombre UNIQUE (nombre)
    );
END;
GO

IF OBJECT_ID('dbo.requerimientos', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.requerimientos (
        id_requerimiento INT IDENTITY(1,1) NOT NULL,
        codigo VARCHAR(30) NOT NULL,
        id_campania INT NOT NULL,
        id_puesto INT NOT NULL,
        cantidad INT NOT NULL,
        dias_capacitacion INT NOT NULL,
        fecha_ingreso DATE NOT NULL,
        fecha_inicio_capacitacion DATE NOT NULL,
        fecha_fin_capacitacion DATE NOT NULL,
        comentarios VARCHAR(255) NULL,
        estado VARCHAR(20) NOT NULL CONSTRAINT df_requerimientos_estado DEFAULT 'ABIERTO',
        creado_por_usuario_id INT NULL,
        created_at DATETIME2(0) NOT NULL CONSTRAINT df_requerimientos_created_at DEFAULT SYSDATETIME(),
        updated_at DATETIME2(0) NULL,
        CONSTRAINT pk_requerimientos PRIMARY KEY (id_requerimiento),
        CONSTRAINT uq_requerimientos_codigo UNIQUE (codigo),
        CONSTRAINT chk_requerimientos_estado CHECK (estado IN ('ABIERTO','CERRADO')),
        CONSTRAINT chk_requerimientos_cantidad CHECK (cantidad > 0),
        CONSTRAINT chk_requerimientos_dias_capacitacion CHECK (dias_capacitacion > 0),
        CONSTRAINT chk_requerimientos_fechas_orden CHECK (fecha_fin_capacitacion < fecha_ingreso),
        CONSTRAINT chk_requerimientos_fechas_capacitacion CHECK (DATEDIFF(DAY, fecha_inicio_capacitacion, fecha_fin_capacitacion) >= 3),
        CONSTRAINT fk_requerimientos_campanias FOREIGN KEY (id_campania) REFERENCES dbo.campanias(id_campania),
        CONSTRAINT fk_requerimientos_puestos FOREIGN KEY (id_puesto) REFERENCES dbo.puestos(id_puesto),
        CONSTRAINT fk_requerimientos_usuarios FOREIGN KEY (creado_por_usuario_id) REFERENCES dbo.usuarios(id_usuario)
    );
END;
GO

IF OBJECT_ID('dbo.postulantes', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.postulantes (
        id_postulante INT IDENTITY(1,1) NOT NULL,
        dni CHAR(8) NOT NULL,
        nombre VARCHAR(80) NOT NULL,
        apellido VARCHAR(80) NOT NULL,
        correo VARCHAR(120) NOT NULL,
        telefono VARCHAR(15) NOT NULL,
        medio_preferido VARCHAR(20) NOT NULL CONSTRAINT df_postulantes_medio_preferido DEFAULT 'whatsapp',
        created_at DATETIME2(0) NOT NULL CONSTRAINT df_postulantes_created_at DEFAULT SYSDATETIME(),
        updated_at DATETIME2(0) NULL,
        CONSTRAINT pk_postulantes PRIMARY KEY (id_postulante),
        CONSTRAINT uq_postulantes_dni UNIQUE (dni),
        CONSTRAINT chk_postulantes_dni CHECK (dni NOT LIKE '%[^0-9]%' AND LEN(dni) = 8),
        CONSTRAINT chk_postulantes_medio_preferido CHECK (medio_preferido IN ('whatsapp','llamada','email'))
    );
END;
GO

IF OBJECT_ID('dbo.postulaciones', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.postulaciones (
        id_postulacion INT IDENTITY(1,1) NOT NULL,
        id_requerimiento INT NOT NULL,
        id_postulante INT NOT NULL,
        cv_url VARCHAR(500) NOT NULL,
        comentarios VARCHAR(500) NULL,
        apto BIT NOT NULL CONSTRAINT df_postulaciones_apto DEFAULT 0,
        entrevista_aprobada BIT NOT NULL CONSTRAINT df_postulaciones_entrevista DEFAULT 0,
        contratar BIT NOT NULL CONSTRAINT df_postulaciones_contratar DEFAULT 0,
        fecha_postulacion DATETIME2(0) NOT NULL CONSTRAINT df_postulaciones_fecha_postulacion DEFAULT SYSDATETIME(),
        fecha_contratacion DATETIME2(0) NULL,
        updated_at DATETIME2(0) NULL,
        CONSTRAINT pk_postulaciones PRIMARY KEY (id_postulacion),
        CONSTRAINT uq_postulaciones_requerimiento_postulante UNIQUE (id_requerimiento, id_postulante),
        CONSTRAINT fk_postulaciones_requerimientos FOREIGN KEY (id_requerimiento) REFERENCES dbo.requerimientos(id_requerimiento),
        CONSTRAINT fk_postulaciones_postulantes FOREIGN KEY (id_postulante) REFERENCES dbo.postulantes(id_postulante),
        CONSTRAINT chk_postulaciones_entrevista_requiere_apto CHECK (entrevista_aprobada = 0 OR apto = 1),
        CONSTRAINT chk_postulaciones_contratar_requiere_entrevista CHECK (contratar = 0 OR entrevista_aprobada = 1),
        CONSTRAINT chk_postulaciones_cv_https CHECK (cv_url LIKE 'https://%')
    );
END;
GO

IF OBJECT_ID('dbo.configuracion_formacion', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.configuracion_formacion (
        id_configuracion INT IDENTITY(1,1) NOT NULL,
        id_requerimiento INT NOT NULL,
        test_count INT NOT NULL CONSTRAINT df_config_formacion_test_count DEFAULT 3,
        aprobacion_promedio DECIMAL(5,2) NOT NULL CONSTRAINT df_config_formacion_aprobacion DEFAULT 14.00,
        created_at DATETIME2(0) NOT NULL CONSTRAINT df_config_formacion_created_at DEFAULT SYSDATETIME(),
        updated_at DATETIME2(0) NULL,
        CONSTRAINT pk_configuracion_formacion PRIMARY KEY (id_configuracion),
        CONSTRAINT uq_configuracion_formacion_requerimiento UNIQUE (id_requerimiento),
        CONSTRAINT fk_configuracion_formacion_requerimientos FOREIGN KEY (id_requerimiento) REFERENCES dbo.requerimientos(id_requerimiento),
        CONSTRAINT chk_configuracion_formacion_test_count CHECK (test_count BETWEEN 1 AND 5),
        CONSTRAINT chk_configuracion_formacion_aprobacion CHECK (aprobacion_promedio BETWEEN 0 AND 20)
    );
END;
GO

IF OBJECT_ID('dbo.evaluaciones_formacion', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.evaluaciones_formacion (
        id_evaluacion INT IDENTITY(1,1) NOT NULL,
        id_postulacion INT NOT NULL,
        nro_evaluacion INT NOT NULL,
        nota DECIMAL(5,2) NOT NULL,
        created_at DATETIME2(0) NOT NULL CONSTRAINT df_evaluaciones_formacion_created_at DEFAULT SYSDATETIME(),
        updated_at DATETIME2(0) NULL,
        CONSTRAINT pk_evaluaciones_formacion PRIMARY KEY (id_evaluacion),
        CONSTRAINT uq_evaluaciones_formacion_postulacion_nro UNIQUE (id_postulacion, nro_evaluacion),
        CONSTRAINT fk_evaluaciones_formacion_postulaciones FOREIGN KEY (id_postulacion) REFERENCES dbo.postulaciones(id_postulacion),
        CONSTRAINT chk_evaluaciones_formacion_nro CHECK (nro_evaluacion BETWEEN 1 AND 5),
        CONSTRAINT chk_evaluaciones_formacion_nota CHECK (nota BETWEEN 0 AND 20)
    );
END;
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'ix_requerimientos_estado' AND object_id = OBJECT_ID('dbo.requerimientos'))
    CREATE INDEX ix_requerimientos_estado ON dbo.requerimientos(estado);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'ix_requerimientos_campania' AND object_id = OBJECT_ID('dbo.requerimientos'))
    CREATE INDEX ix_requerimientos_campania ON dbo.requerimientos(id_campania);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'ix_postulaciones_requerimiento' AND object_id = OBJECT_ID('dbo.postulaciones'))
    CREATE INDEX ix_postulaciones_requerimiento ON dbo.postulaciones(id_requerimiento);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'ix_postulaciones_postulante' AND object_id = OBJECT_ID('dbo.postulaciones'))
    CREATE INDEX ix_postulaciones_postulante ON dbo.postulaciones(id_postulante);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'ix_evaluaciones_postulacion' AND object_id = OBJECT_ID('dbo.evaluaciones_formacion'))
    CREATE INDEX ix_evaluaciones_postulacion ON dbo.evaluaciones_formacion(id_postulacion);
GO

