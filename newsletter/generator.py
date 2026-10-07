import os
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

def generate_newsletter_html(stories, trend_data):
    """
    Generate the HTML newsletter from the analyzed stories.
    """
    env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
    template = env.get_template('email.html')
    
    # Categorize stories
    india_stories = [s for s in stories if s['analysis_data'].get('geography', '').lower() == 'india']
    global_stories = [s for s in stories if s['analysis_data'].get('geography', '').lower() != 'india']
    
    top_stories = stories[:3] if len(stories) >= 3 else stories
    
    # Extract one MBA takeaway (take the best one from top stories)
    mba_takeaway = None
    for s in stories:
        if s['analysis_data'].get('mba_lens') and s['analysis_data']['mba_lens'].get('concept'):
            mba_takeaway = s['analysis_data']['mba_lens']
            break
            
    # Extract numbers
    meaningful_numbers = []
    for s in stories:
        if s['analysis_data'].get('meaningful_numbers'):
            meaningful_numbers.extend(s['analysis_data']['meaningful_numbers'])
            
    html_content = template.render(
        date=datetime.now().strftime("%B %d, %Y"),
        top_stories=top_stories,
        india_stories=india_stories,
        global_stories=global_stories,
        trend_data=trend_data,
        mba_takeaway=mba_takeaway,
        meaningful_numbers=meaningful_numbers[:5] # Limit to 5
    )
    
    return html_content
