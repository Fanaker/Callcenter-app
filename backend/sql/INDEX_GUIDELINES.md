# Index Guidelines & Performance Tuning

Complete guide for managing and monitoring indexes in Recruitment Database.

## 📊 Index Summary

**Total Indexes Created**: 17

### By Table

| Table | Count | Purpose |
|-------|-------|---------|
| campanias | 1 | Filter active campaigns |
| puestos | 1 | Filter active positions |
| requerimientos | 5 | State filters, lookup, join performance |
| postulantes | 3 | DNI/email lookup, name search |
| postulaciones | 7 | State transitions, duplicate detection, sorting |

---

## 🎯 Index Purposes

### 1. Unique Indexes (Enforce Uniqueness)

```sql
idx_requerimientos_codigo          -- codigo UNIQUE
idx_postulantes_dni                -- dni UNIQUE
idx_postulantes_email              -- email UNIQUE
```

**Purpose**: Enforce unique constraints + provide fast lookup  
**Impact**: 90%+ performance improvement on lookups

### 2. Filtered Indexes (Reduce Size)

```sql
idx_campanias_activa               -- WHERE activa = 1
idx_puestos_activo                 -- WHERE activo = 1
idx_postulaciones_estado_activas   -- WHERE estado NOT IN (...)
```

**Purpose**: Only index relevant rows (active records)  
**Impact**: 50% smaller indexes, faster scans

### 3. Covering Indexes (Eliminate Lookups)

```sql
idx_postulaciones_estado           -- INCLUDE (many columns)
idx_postulaciones_workflow_covering -- INCLUDE (all needed columns)
```

**Purpose**: All columns needed for query in index  
**Impact**: Avoid table lookups, 95%+ improvement

### 4. Composite Indexes (Multi-Column Filters)

```sql
idx_requerimientos_campania_estado    -- (id_campania, estado)
idx_postulaciones_requerimiento_postulante -- (id_requerimiento, id_postulante)
```

**Purpose**: Optimize combined filters  
**Impact**: 80-90% improvement on multi-column queries

---

## ⚡ Query → Index Mapping

### GET Endpoints

| Endpoint | Query | Index Used |
|----------|-------|------------|
| GET /campanias/activas | `WHERE activa = 1` | `idx_campanias_activa` |
| GET /puestos/activos | `WHERE activo = 1` | `idx_puestos_activo` |
| GET /requerimientos | `WHERE estado = ?` | `idx_requerimientos_estado` |
| GET /requerimientos | `WHERE id_campania = ?` | `idx_requerimientos_campania` |
| GET /requerimientos/{codigo} | `WHERE codigo = ?` | `idx_requerimientos_codigo` |
| GET /req/{codigo}/postulaciones | `WHERE id_requerimiento = ?` | `idx_postulaciones_id_requerimiento` |

### POST Endpoints

| Endpoint | Query | Index Used |
|----------|-------|------------|
| POST /requerimientos | FK check `id_campania` | `idx_requerimientos_campania` |
| POST /postulaciones | Duplicate check | `idx_postulaciones_requerimiento_postulante` |
| POST /postulaciones | DNI lookup | `idx_postulantes_dni` |

### PUT Endpoints

| Endpoint | Query | Index Used |
|----------|-------|------------|
| PUT /postulaciones/{id}/* | State lookup | `idx_postulaciones_id_estado` |
| PUT /postulaciones/{id}/* | Get application | `idx_postulaciones_workflow_covering` |

---

## 📈 Expected Performance Improvements

### Before Indexes (Full Table Scans)

```
GET /campanias/activas        ~ 200-500ms (1000+ rows scanned)
GET /requerimientos            ~ 300-800ms (10000+ rows scanned)
POST /postulaciones (dup check) ~ 400-1000ms (100000+ rows checked)
```

### After Indexes

```
GET /campanias/activas        ~ 5-10ms    (95% improvement ✅)
GET /requerimientos            ~ 20-50ms   (85% improvement ✅)
POST /postulaciones (dup check) ~ 30-80ms   (85% improvement ✅)
```

---

## 🔍 Monitoring Indexes

### 1. View All Indexes

```sql
SELECT
    i.name AS IndexName,
    t.name AS TableName,
    c.name AS ColumnName
FROM sys.indexes i
INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id
                                 AND i.index_id = ic.index_id
INNER JOIN sys.columns c ON ic.object_id = c.object_id
                          AND ic.column_id = c.column_id
INNER JOIN sys.tables t ON i.object_id = t.object_id
WHERE t.name IN ('campanias', 'puestos', 'requerimientos', 'postulantes', 'postulaciones')
ORDER BY t.name, i.name;
```

### 2. Check Index Fragmentation

```sql
SELECT
    OBJECT_NAME(ps.object_id) AS TableName,
    i.name AS IndexName,
    ps.avg_fragmentation_in_percent AS FragmentationPercent,
    ps.page_count AS PageCount,
    CASE
        WHEN ps.avg_fragmentation_in_percent < 10 THEN 'OK - No maintenance'
        WHEN ps.avg_fragmentation_in_percent < 30 THEN 'REORGANIZE'
        ELSE 'REBUILD'
    END AS Action
FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') ps
INNER JOIN sys.indexes i ON ps.object_id = i.object_id
                         AND ps.index_id = i.index_id
WHERE ps.index_id > 0
  AND ps.page_count > 1000
  AND OBJECT_NAME(ps.object_id) IN ('campanias', 'puestos', 'requerimientos', 'postulantes', 'postulaciones')
ORDER BY ps.avg_fragmentation_in_percent DESC;
```

### 3. View Index Usage Statistics

```sql
SELECT
    OBJECT_NAME(i.object_id) AS TableName,
    i.name AS IndexName,
    COALESCE(s.user_seeks, 0) AS SeekCount,
    COALESCE(s.user_scans, 0) AS ScanCount,
    COALESCE(s.user_lookups, 0) AS LookupCount,
    COALESCE(s.user_updates, 0) AS UpdateCount,
    COALESCE(s.user_seeks, 0) + COALESCE(s.user_scans, 0) + COALESCE(s.user_lookups, 0) AS TotalUses
FROM sys.indexes i
LEFT JOIN sys.dm_db_index_usage_stats s ON i.object_id = s.object_id
                                        AND i.index_id = s.index_id
                                        AND s.database_id = DB_ID()
WHERE i.index_id > 0
  AND OBJECT_NAME(i.object_id) IN ('campanias', 'puestos', 'requerimientos', 'postulantes', 'postulaciones')
ORDER BY TotalUses DESC;
```

### 4. Find Unused Indexes

```sql
SELECT
    OBJECT_NAME(i.object_id) AS TableName,
    i.name AS IndexName,
    COALESCE(s.user_seeks, 0) AS SeekCount,
    COALESCE(s.user_scans, 0) AS ScanCount,
    COALESCE(s.user_lookups, 0) AS LookupCount,
    COALESCE(s.user_updates, 0) AS UpdateCount
FROM sys.indexes i
LEFT JOIN sys.dm_db_index_usage_stats s ON i.object_id = s.object_id
                                        AND i.index_id = s.index_id
                                        AND s.database_id = DB_ID()
WHERE i.index_id > 0
  AND OBJECT_NAME(i.object_id) IN ('campanias', 'puestos', 'requerimientos', 'postulantes', 'postulaciones')
  AND COALESCE(s.user_seeks, 0) + COALESCE(s.user_scans, 0) + COALESCE(s.user_lookups, 0) = 0
ORDER BY COALESCE(s.user_updates, 0) DESC;
```

---

## 🛠️ Index Maintenance

### Weekly: Reorganize Fragmented Indexes

```sql
-- Reorganize indexes with 10-30% fragmentation
DECLARE @TableName NVARCHAR(128);
DECLARE cur CURSOR FOR
    SELECT DISTINCT OBJECT_NAME(ps.object_id)
    FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') ps
    INNER JOIN sys.indexes i ON ps.object_id = i.object_id AND ps.index_id = i.index_id
    WHERE ps.avg_fragmentation_in_percent BETWEEN 10 AND 30
      AND ps.page_count > 1000;

OPEN cur;
FETCH NEXT FROM cur INTO @TableName;
WHILE @@FETCH_STATUS = 0
BEGIN
    DBCC SHOWCONTIG (@TableName);
    DBCC DBREINDEX (@TableName);
    FETCH NEXT FROM cur INTO @TableName;
END;
CLOSE cur;
DEALLOCATE cur;
```

### Monthly: Rebuild Highly Fragmented Indexes

```sql
-- Rebuild indexes with >30% fragmentation
ALTER INDEX idx_postulaciones_estado ON postulaciones REBUILD;
ALTER INDEX idx_postulaciones_id_postulante ON postulaciones REBUILD;
ALTER INDEX idx_requerimientos_estado ON requerimientos REBUILD;

-- Update statistics after rebuild
UPDATE STATISTICS postulaciones;
UPDATE STATISTICS requerimientos;
```

### As Needed: Update Statistics

```sql
-- Update statistics for all tables
UPDATE STATISTICS campanias;
UPDATE STATISTICS puestos;
UPDATE STATISTICS requerimientos;
UPDATE STATISTICS postulantes;
UPDATE STATISTICS postulaciones;
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: Slow Query Despite Index

**Symptoms**: Query still slow even with index

**Solution**:
```sql
-- Check index fragmentation
SELECT * FROM sys.dm_db_index_physical_stats(DB_ID(), OBJECT_ID('table_name'), NULL, NULL, 'LIMITED');

-- If fragmented, rebuild
ALTER INDEX index_name ON table_name REBUILD;

-- Update statistics
UPDATE STATISTICS table_name;
```

### Issue 2: Duplicate Index

**Symptoms**: Multiple indexes on same column

**Solution**:
```sql
-- Find duplicate indexes
SELECT i1.name, i2.name FROM sys.indexes i1, sys.indexes i2
WHERE i1.object_id = i2.object_id
  AND i1.name < i2.name
  AND (SELECT COUNT(*) FROM sys.index_columns WHERE index_id = i1.index_id)
    = (SELECT COUNT(*) FROM sys.index_columns WHERE index_id = i2.index_id);

-- Drop unused index
DROP INDEX duplicate_index ON table_name;
```

### Issue 3: Index Consuming Too Much Space

**Symptoms**: Database size growing unexpectedly

**Solution**:
```sql
-- Check index sizes
SELECT
    i.name AS IndexName,
    SUM(ps.used_page_count) * 8 / 1024 AS SizeMB
FROM sys.indexes i
INNER JOIN sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') ps
    ON i.object_id = ps.object_id AND i.index_id = ps.index_id
WHERE i.index_id > 0
GROUP BY i.name
ORDER BY SizeMB DESC;

-- Remove unused large indexes
DROP INDEX large_unused_index ON table_name;
```

---

## 📅 Maintenance Schedule

### Daily
- Monitor slow query log
- Check for blocking queries

### Weekly
- Reorganize indexes with 10-30% fragmentation
- Review index usage statistics

### Monthly
- Rebuild indexes with >30% fragmentation
- Update all statistics
- Review execution plans for slow queries

### Quarterly
- Analyze index efficiency
- Remove unused indexes
- Consider new indexes for frequent queries

---

## 🚀 Performance Tuning Tips

### 1. Use Execution Plans

```
-- In SQL Server Management Studio:
1. Tools → Options → Query Results → SQL Server → Results to Grid → Include actual execution plan
2. Run query
3. Click "Execution Plan" tab
4. Look for index scans → should be index seeks
```

### 2. Monitor Query Performance

```sql
-- Create index on frequently run query
SELECT DISTINCT queries_count, last_execution_time, query_text
FROM sys.dm_exec_query_stats;
```

### 3. Test Index Changes

```
-- Always test on staging/development database first
-- Measure performance before & after
-- Monitor for 24+ hours
-- Then deploy to production
```

### 4. Document Changes

```
-- Keep audit log of index changes
-- Record reason for each index
-- Track performance improvements
```

---

## 📊 Current Database Statistics

Based on expected data volume:

```
Typical Data:
- Campanias:     10-50 rows
- Puestos:       20-100 rows
- Requerimientos: 100-500 rows
- Postulantes:   1,000-50,000 rows
- Postulaciones: 5,000-250,000 rows

Index Impact:
- Disk Space:    +200-300MB
- Write Cost:    +5-10% (INSERT/UPDATE)
- Read Benefit:  +80-95% (SELECT)
```

---

## ✅ Verification Checklist

After deploying indexes:

- [ ] All 17 indexes created successfully
- [ ] No duplicate indexes exist
- [ ] Fragmentation < 10% for active indexes
- [ ] Query performance improved (measure with execution plans)
- [ ] No unexpected slow queries in error logs
- [ ] Disk space within expectations
- [ ] Statistics updated
- [ ] Maintenance jobs scheduled

---

## 📚 References

- [SQL Server Index Design Guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide)
- [sys.dm_db_index_physical_stats](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-db-index-physical-stats-transact-sql)
- [Index Fragmentation Monitoring](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/monitor-and-tune-for-performance)

---

**Last Updated**: May 2026  
**Version**: 1.0  
**Database**: SQL Server (RDS)
