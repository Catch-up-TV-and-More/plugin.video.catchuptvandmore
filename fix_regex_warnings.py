#!/usr/bin/env python3
"""
Script pour corriger automatiquement les séquences d'échappement invalides 
dans les expressions régulières du projet Catch-up TV & More.
"""

import os
import re
import sys

def fix_regex_patterns_in_file(filepath):
    """Corrige les patterns regex dans un fichier donné."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = False
        
        # Pattern pour détecter re.compile avec string normale au lieu de raw string
        # Recherche les re.compile('...') qui contiennent des échappements problématiques
        regex_patterns = re.finditer(r"re\.compile\('([^']*(?:\\[^'\\]*)*[^']*)'\)", content)
        
        replacements = []
        for match in regex_patterns:
            full_match = match.group(0)
            pattern_content = match.group(1)
            
            # Vérifier si le pattern contient des échappements qui nécessitent une raw string
            problematic_sequences = [
                r'\?', r'\.', r'\/', r'\&', r'\=', r'\:', r'\;', r'\%', r'\|', r'\{'
            ]
            
            needs_fix = any(seq in pattern_content for seq in problematic_sequences)
            
            if needs_fix:
                # Remplacer par une raw string
                new_pattern = f"re.compile(r'{pattern_content}')"
                replacements.append((full_match, new_pattern))
                changes_made = True
        
        # Appliquer les remplacements
        for old, new in replacements:
            content = content.replace(old, new, 1)
        
        # Sauvegarder si des changements ont été faits
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Corrigé: {filepath}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Erreur avec {filepath}: {e}")
        return False

def main():
    """Fonction principale pour traiter tous les fichiers Python."""
    project_root = "/workspaces/plugin.video.catchuptvandmore"
    
    # Trouver tous les fichiers Python
    python_files = []
    for root, dirs, files in os.walk(project_root):
        # Exclure certains dossiers
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Traitement de {len(python_files)} fichiers Python...")
    
    fixed_count = 0
    for filepath in python_files:
        if fix_regex_patterns_in_file(filepath):
            fixed_count += 1
    
    print(f"\n🎉 Terminé! {fixed_count} fichiers ont été corrigés.")

if __name__ == "__main__":
    main()
