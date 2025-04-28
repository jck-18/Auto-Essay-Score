import os
import shutil
import sys

def create_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def copy_file(src, dst):
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Copied: {src} -> {dst}")
    else:
        print(f"Source file not found: {src}")

def main():
    # Create necessary directories
    create_dir_if_not_exists('api/templates')
    create_dir_if_not_exists('api/static')
    
    # Copy files to api directory
    files_to_copy = [
        ('gemma_scorer.py', 'api/gemma_scorer.py'),
        ('model.h5', 'api/model.h5'),
        ('tokenizer.pickle', 'api/tokenizer.pickle'),
        ('word2vec.magnitude', 'api/word2vec.magnitude'),
    ]
    
    for src, dst in files_to_copy:
        copy_file(src, dst)
    
    # Copy template files
    template_files = os.listdir('templates')
    for file in template_files:
        copy_file(os.path.join('templates', file), os.path.join('api/templates', file))
    
    # Copy static files if they exist
    if os.path.exists('static'):
        static_files = os.listdir('static')
        for file in static_files:
            src = os.path.join('static', file)
            dst = os.path.join('api/static', file)
            if os.path.isfile(src):
                copy_file(src, dst)
    
    print("\nFiles copied successfully for Vercel deployment!")
    print("Make sure to set the OPENROUTER_API_KEY environment variable in your Vercel project settings.")

if __name__ == "__main__":
    main() 