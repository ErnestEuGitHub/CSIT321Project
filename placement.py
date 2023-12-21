def get_updated_content():
    # Logic to read and return updated content from seeding.html
    with open('templates\seeding.html', 'r') as file:   
        updated_content = file.read()
    return updated_content