# Migration / 迁移
Skill 1.0.0 and schema 1.0 are distinct. `migrate --path VAULT --to-schema 1.0 --dry-run` validates a no-op. Unknown target schemas are refused; no fabricated 2.0 migration. Future schema changes require explicit, reversible, tested migration and human-approved backup. Installation never migrates vaults.
升级不静默改写私人档案；保存旧技能目录可回退代码，数据回滚另用 rollback。
