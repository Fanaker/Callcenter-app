USE CallCenter;
GO

CREATE OR ALTER VIEW dbo.vw_requerimientos_frontend
AS
SELECT
    r.id_requerimiento AS idRequerimiento,
    r.codigo,
    r.id_campania AS campaniaId,
    c.nombre AS campaign,
    r.id_puesto AS puestoId,
    p.nombre AS puesto,
    r.cantidad,
    r.dias_capacitacion AS diasCapacitacion,
    CONVERT(VARCHAR(10), r.fecha_ingreso, 23) AS fechaIngreso,
    CONVERT(VARCHAR(10), r.fecha_inicio_capacitacion, 23) AS fechaInicioCapacitacion,
    CONVERT(VARCHAR(10), r.fecha_fin_capacitacion, 23) AS fechaFinCapacitacion,
    r.comentarios,
    r.estado,
    ISNULL(cf.test_count, 3) AS testCount,
    ISNULL(cf.aprobacion_promedio, 14.00) AS aprobacionPromedio,
    r.created_at AS createdAt,
    r.updated_at AS updatedAt
FROM dbo.requerimientos r
INNER JOIN dbo.campanias c ON c.id_campania = r.id_campania
INNER JOIN dbo.puestos p ON p.id_puesto = r.id_puesto
LEFT JOIN dbo.configuracion_formacion cf ON cf.id_requerimiento = r.id_requerimiento;
GO

CREATE OR ALTER VIEW dbo.vw_postulaciones_frontend
AS
SELECT
    po.id_postulacion AS idPostulacion,
    po.id_requerimiento AS idRequerimiento,
    r.codigo AS rqCodigo,
    pt.id_postulante AS idPostulante,
    pt.dni,
    pt.nombre,
    pt.apellido,
    pt.correo,
    pt.telefono,
    pt.medio_preferido AS medioPreferido,
    po.cv_url AS cvUrl,
    po.comentarios,
    CAST(po.apto AS BIT) AS apto,
    CAST(po.entrevista_aprobada AS BIT) AS entrevistaAprobada,
    CAST(CASE WHEN po.apto = 1 AND po.entrevista_aprobada = 1 THEN 1 ELSE 0 END AS BIT) AS elegido,
    CAST(po.contratar AS BIT) AS contratar,
    po.fecha_postulacion AS fechaPostulacion,
    po.fecha_contratacion AS fechaContratacion,
    CAST(ISNULL(MAX(CASE WHEN ef.nro_evaluacion = 1 THEN ef.nota END), 0) AS DECIMAL(5,2)) AS test1,
    CAST(ISNULL(MAX(CASE WHEN ef.nro_evaluacion = 2 THEN ef.nota END), 0) AS DECIMAL(5,2)) AS test2,
    CAST(ISNULL(MAX(CASE WHEN ef.nro_evaluacion = 3 THEN ef.nota END), 0) AS DECIMAL(5,2)) AS test3,
    CAST(ISNULL(MAX(CASE WHEN ef.nro_evaluacion = 4 THEN ef.nota END), 0) AS DECIMAL(5,2)) AS test4,
    CAST(ISNULL(MAX(CASE WHEN ef.nro_evaluacion = 5 THEN ef.nota END), 0) AS DECIMAL(5,2)) AS test5
FROM dbo.postulaciones po
INNER JOIN dbo.requerimientos r ON r.id_requerimiento = po.id_requerimiento
INNER JOIN dbo.postulantes pt ON pt.id_postulante = po.id_postulante
LEFT JOIN dbo.evaluaciones_formacion ef ON ef.id_postulacion = po.id_postulacion
GROUP BY
    po.id_postulacion, po.id_requerimiento, r.codigo,
    pt.id_postulante, pt.dni, pt.nombre, pt.apellido, pt.correo, pt.telefono, pt.medio_preferido,
    po.cv_url, po.comentarios, po.apto, po.entrevista_aprobada, po.contratar,
    po.fecha_postulacion, po.fecha_contratacion;
GO
