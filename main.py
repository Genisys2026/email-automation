import asyncio
from aiohttp import web
from api.email_routes import setup_email_routes
from api.slack_routes import setup_slack_routes
from api.sfdc_routes import setup_sfdc_routes
from api.followup_routes import setup_followup_routes
from config.settings import load_config
from slack_review.client import SlackClient
from sfdc_integration.client import SFDCClient
from email_handling.client import EmailClient
from tracking.activity_tracker import ActivityTracker
from core.followup_manager import FollowupManager

async def init_app():
    app = web.Application()
    config = load_config()
    
    # Initialize clients
    slack_client = SlackClient(config['slack'])
    sfdc_client = SFDCClient(config['sfdc'])
    email_client = EmailClient(config['email'])
    activity_tracker = ActivityTracker(config['tracking'])
    followup_manager = FollowupManager(config['followup'])
    
    # Store clients in app context
    app['config'] = config
    app['slack_client'] = slack_client
    app['sfdc_client'] = sfdc_client
    app['email_client'] = email_client
    app['activity_tracker'] = activity_tracker
    app['followup_manager'] = followup_manager
    
    # Setup routes
    setup_email_routes(app)
    setup_slack_routes(app)
    setup_sfdc_routes(app)
    setup_followup_routes(app)
    
    # Setup background tasks
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    
    return app

async def start_background_tasks(app):
    app['followup_checker'] = asyncio.create_task(
        app['followup_manager'].run_followup_checks(app)
    )
    app['email_poller'] = asyncio.create_task(
        app['email_client'].poll_emails(app)
    )

async def cleanup_background_tasks(app):
    app['followup_checker'].cancel()
    app['email_poller'].cancel()
    await asyncio.gather(
        app['followup_checker'],
        app['email_poller'],
        return_exceptions=True
    )

if __name__ == '__main__':
    asyncio.run(web._run_app(init_app(), host='0.0.0.0', port=8080))

