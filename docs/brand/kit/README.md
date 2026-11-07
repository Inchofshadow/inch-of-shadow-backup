# Versioned copy of the brand kit skill

The live skill is `Inch of Shadow/.claude/skills/brand/` (the `.claude` folder is not under
version control, so this copy exists to keep its history and to restore it).

Refresh this copy after changing the live skill:

    cp -R "../../../../.claude/skills/brand/" .      # run from this folder

Restore the live skill from this copy:

    mkdir -p "../../../../.claude/skills/brand" && cp -R SKILL.md references scripts "../../../../.claude/skills/brand/"
