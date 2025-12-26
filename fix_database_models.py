#!/usr/bin/env python3
"""
Fix database.py to wrap ORM models in conditional block.
This allows the file to be imported even when DATABASE_URL is not set.
"""

def fix_database_file():
    with open('backend/services/database.py', 'r') as f:
        content = f.read()
    
    # Find the models section
    models_start_marker = '\n\n# ORM Models\nclass User(Base):'
    models_end_marker = '\n\n# Database initialization\ndef init_database():'
    
    if models_start_marker not in content:
        print("❌ Could not find models start marker")
        return False
    
    if models_end_marker not in content:
        print("❌ Could not find models end marker")
        return False
    
    # Split content
    before_models = content[:content.index(models_start_marker)]
    models_section_start = content.index(models_start_marker) + 2  # Skip the two newlines
    models_section_end = content.index(models_end_marker)
    models_section = content[models_section_start:models_section_end]
    after_models = content[models_section_end:]
    
    # Indent the models section
    indented_lines = []
    for line in models_section.split('\n'):
        if line:  # Only indent non-empty lines
            indented_lines.append('    ' + line)
        else:
            indented_lines.append(line)
    indented_models = '\n'.join(indented_lines)
    
    # Construct new content
    new_content = before_models + '\n\n'
    new_content += '# ORM Models - only define if database is available\n'
    new_content += 'if DATABASE_AVAILABLE and Base is not None:\n'
    new_content += indented_models
    new_content += '\nelse:\n'
    new_content += '    # Define placeholder values when database is not available\n'
    new_content += '    User = None\n'
    new_content += '    Session = None\n'
    new_content += '    SearchHistory = None\n'
    new_content += '    Favorite = None\n'
    new_content += '    CustomList = None\n'
    new_content += '    UserSettings = None\n'
    new_content += after_models
    
    # Write back
    with open('backend/services/database.py', 'w') as f:
        f.write(new_content)
    
    print("✅ database.py fixed successfully")
    return True

if __name__ == '__main__':
    fix_database_file()
