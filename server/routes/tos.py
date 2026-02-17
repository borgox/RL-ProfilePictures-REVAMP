import logging
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Legal"])


@router.get("/tos", response_class=HTMLResponse)
async def get_terms_of_service():
    """Get Terms of Service page."""
    return HTMLResponse(content=get_tos_html())


@router.get("/privacy", response_class=HTMLResponse)
async def get_privacy_policy():
    """Get Privacy Policy page."""
    return HTMLResponse(content=get_privacy_html())


def get_tos_html() -> str:
    """Generate Terms of Service HTML page."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Terms of Service - RLProfilePicturesREVAMP API</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
            }
            
            .content {
                background: white;
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            }
            
            h1 {
                color: #2c3e50;
                margin-bottom: 30px;
                text-align: center;
                font-size: 2.5rem;
            }
            
            h2 {
                color: #34495e;
                margin-top: 30px;
                margin-bottom: 15px;
                font-size: 1.5rem;
                border-bottom: 2px solid #3498db;
                padding-bottom: 5px;
            }
            
            h3 {
                color: #2c3e50;
                margin-top: 20px;
                margin-bottom: 10px;
                font-size: 1.2rem;
            }
            
            p {
                margin-bottom: 15px;
                text-align: justify;
            }
            
            ul {
                margin-left: 20px;
                margin-bottom: 15px;
            }
            
            li {
                margin-bottom: 8px;
            }
            
            .highlight {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 5px;
                padding: 15px;
                margin: 20px 0;
            }
            
            .warning {
                background: #f8d7da;
                border: 1px solid #f5c6cb;
                border-radius: 5px;
                padding: 15px;
                margin: 20px 0;
            }
            
            .footer {
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                color: #666;
            }
            
            .back-link {
                display: inline-block;
                background: #3498db;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-bottom: 20px;
                transition: background 0.3s ease;
            }
            
            .back-link:hover {
                background: #2980b9;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content">
                <a href="/" class="back-link">← Back to API</a>
                
                <h1>Terms of Service</h1>
                
                <p><strong>Last Updated:</strong> September 2025</p>
                
                <div class="highlight">
                    <strong>Important:</strong> By using the RLProfilePicturesREVAMP API, you agree to these terms and conditions. 
                    Please read them carefully.
                </div>
                
                <h2>1. Service Description</h2>
                <p>
                    The RLProfilePicturesREVAMP API provides avatar image retrieval and caching services for various gaming platforms 
                    including Steam, Xbox Live, PlayStation Network, Nintendo Switch, and Epic Games. The service processes 
                    and optimizes avatar images for consistent delivery.
                </p>
                
                <div class="highlight">
                    <strong>Primary Usage:</strong> This API is primarily used (99.9% of the time) by the BakkesMod plugin 
                    "RLProfilePicturesREVAMP" to enhance the Rocket League gaming experience by displaying user avatars 
                    from various gaming platforms within the game interface.
                </div>
                
                <h2>2. Data Collection and Tracking</h2>
                <p>
                    To provide and improve our services, we collect and track the following information:
                </p>
                <ul>
                    <li><strong>Request Data:</strong> Platform, user ID, request timestamps, response times</li>
                    <li><strong>Technical Data:</strong> IP addresses, user agents, referrer information</li>
                    <li><strong>Usage Analytics:</strong> Request patterns, platform preferences, error logs</li>
                    <li><strong>Performance Metrics:</strong> Cache hit rates, response times, bandwidth usage</li>
                </ul>
                
                <div class="warning">
                    <strong>Privacy Notice:</strong> We use this data for service optimization, debugging, and analytics. 
                    IP addresses are used for rate limiting and abuse prevention. We do not sell personal data to third parties.
                </div>
                
                <h2>3. Acceptable Use</h2>
                <p>You agree to use the API responsibly and not to:</p>
                <ul>
                    <li>Exceed rate limits (40 requests per minute per IP)</li>
                    <li>Use the service for illegal or unauthorized purposes</li>
                    <li>Attempt to reverse engineer or exploit the API</li>
                    <li>Use automated tools that may overload our servers</li>
                    <li>Violate any gaming platform's terms of service</li>
                    <li>Use the API outside of the intended BakkesMod plugin context without permission</li>
                </ul>
                
                <div class="highlight">
                    <strong>BakkesMod Integration:</strong> This API is specifically designed for use with the 
                    RLProfilePicturesREVAMP BakkesMod plugin. While other uses are not explicitly prohibited, 
                    the service is optimized for this specific use case and may not function optimally for other purposes.
                </div>
                
                <h2>4. Rate Limiting</h2>
                <p>
                    We implement rate limiting to ensure fair usage and service stability. Current limits are:
                </p>
                <ul>
                    <li>40 requests per minute per IP address</li>
                    <li>Automatic blocking for excessive requests</li>
                    <li>Rate limit resets every minute</li>
                </ul>
                
                <h2>5. Service Availability</h2>
                <p>
                    While we strive for high availability, we do not guarantee 100% uptime. The service may be temporarily 
                    unavailable due to maintenance, updates, or technical issues. We reserve the right to modify or 
                    discontinue the service with reasonable notice.
                </p>
                
                <h2>6. Data Retention</h2>
                <p>
                    We retain request logs and analytics data for debugging and optimization purposes. 
                    Rate limiting data is automatically cleaned up after 24 hours. Other data may be retained 
                    for longer periods as needed for service operation.
                </p>
                
                <h2>7. Intellectual Property</h2>
                <p>
                    Avatar images are the property of their respective gaming platforms. We provide caching and 
                    optimization services but do not claim ownership of the original content. Users must respect 
                    the intellectual property rights of gaming platforms.
                </p>
                
                <h2>8. Limitation of Liability</h2>
                <p>
                    The service is provided "as is" without warranties. We are not liable for any damages arising 
                    from the use of this service, including but not limited to data loss, service interruptions, 
                    or third-party platform changes.
                </p>
                
                <h2>9. Changes to Terms</h2>
                <p>
                    We may update these terms at any time. Continued use of the service after changes constitutes 
                    acceptance of the new terms. We will notify users of significant changes when possible.
                </p>
                
                <h2>10. BakkesMod Plugin Usage</h2>
                <p>
                    This API is specifically designed and optimized for use with the RLProfilePicturesREVAMP BakkesMod plugin. 
                    The plugin enhances the Rocket League gaming experience by displaying user avatars from various gaming 
                    platforms within the game interface.
                </p>
                <ul>
                    <li><strong>Intended Use:</strong> Displaying avatars in Rocket League through BakkesMod</li>
                    <li><strong>Data Processing:</strong> Optimized for real-time avatar retrieval during gameplay</li>
                    <li><strong>Performance:</strong> Designed for low-latency responses suitable for gaming</li>
                    <li><strong>Compatibility:</strong> Works with all major gaming platforms supported by Rocket League</li>
                </ul>
                
                <h2>11. Contact Information</h2>
                <p>
                    For questions about these terms or the service, please contact us through the appropriate channels. 
                    We are committed to addressing user concerns and improving our service based on feedback.
                </p>
                
                <div class="footer">
                    <p>© 2025 RLProfilePicturesREVAMP API. All rights reserved.</p>
                    <p><a href="/privacy">Privacy Policy</a> | <a href="/">API Home</a></p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """


def get_privacy_html() -> str:
    """Generate Privacy Policy HTML page."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Privacy Policy - RLProfilePicturesREVAMP API</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
            }
            
            .content {
                background: white;
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            }
            
            h1 {
                color: #2c3e50;
                margin-bottom: 30px;
                text-align: center;
                font-size: 2.5rem;
            }
            
            h2 {
                color: #34495e;
                margin-top: 30px;
                margin-bottom: 15px;
                font-size: 1.5rem;
                border-bottom: 2px solid #3498db;
                padding-bottom: 5px;
            }
            
            h3 {
                color: #2c3e50;
                margin-top: 20px;
                margin-bottom: 10px;
                font-size: 1.2rem;
            }
            
            p {
                margin-bottom: 15px;
                text-align: justify;
            }
            
            ul {
                margin-left: 20px;
                margin-bottom: 15px;
            }
            
            li {
                margin-bottom: 8px;
            }
            
            .highlight {
                background: #d1ecf1;
                border: 1px solid #bee5eb;
                border-radius: 5px;
                padding: 15px;
                margin: 20px 0;
            }
            
            .footer {
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                color: #666;
            }
            
            .back-link {
                display: inline-block;
                background: #3498db;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-bottom: 20px;
                transition: background 0.3s ease;
            }
            
            .back-link:hover {
                background: #2980b9;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content">
                <a href="/" class="back-link">← Back to API</a>
                
                <h1>Privacy Policy</h1>
                
                <p><strong>Last Updated:</strong> September 2025</p>
                
                <div class="highlight">
                    <strong>Your Privacy Matters:</strong> This privacy policy explains how we collect, use, and protect 
                    your information when using the RLProfilePicturesREVAMP API.
                </div>
                
                <div class="highlight">
                    <strong>Primary Usage Context:</strong> This API is primarily used (99.9% of the time) by the 
                    BakkesMod plugin "RLProfilePicturesREVAMP" to enhance the Rocket League gaming experience by 
                    displaying user avatars from various gaming platforms within the game interface.
                </div>
                
                <h2>1. Information We Collect</h2>
                
                <h3>1.1 Request Information</h3>
                <ul>
                    <li>Gaming platform (Steam, Xbox, PSN, Switch, Epic)</li>
                    <li>User IDs for avatar retrieval</li>
                    <li>Request timestamps and response times</li>
                    <li>Success/failure status and error messages</li>
                </ul>
                
                <h3>1.2 Technical Information</h3>
                <ul>
                    <li>IP addresses for rate limiting and abuse prevention</li>
                    <li>User agent strings for browser/device identification</li>
                    <li>Referrer information (when available)</li>
                    <li>Request headers and metadata</li>
                </ul>
                
                <h3>1.3 Usage Analytics</h3>
                <ul>
                    <li>Request patterns and frequency</li>
                    <li>Platform preferences and usage trends</li>
                    <li>Cache hit rates and performance metrics</li>
                    <li>Error logs and debugging information</li>
                </ul>
                
                <h2>2. How We Use Your Information</h2>
                
                <h3>2.1 Service Operation</h3>
                <ul>
                    <li>Processing avatar requests and caching images</li>
                    <li>Implementing rate limiting to prevent abuse</li>
                    <li>Optimizing response times and performance</li>
                    <li>Debugging technical issues and errors</li>
                </ul>
                
                <h3>2.2 Analytics and Improvement</h3>
                <ul>
                    <li>Understanding usage patterns and trends</li>
                    <li>Identifying popular platforms and features</li>
                    <li>Monitoring service performance and reliability</li>
                    <li>Planning capacity and infrastructure improvements</li>
                </ul>
                
                <h3>2.3 Security and Abuse Prevention</h3>
                <ul>
                    <li>Detecting and preventing malicious activity</li>
                    <li>Implementing rate limiting and access controls</li>
                    <li>Monitoring for unusual usage patterns</li>
                    <li>Protecting service availability for all users</li>
                </ul>
                
                <h2>3. Data Sharing and Disclosure</h2>
                <p>
                    We do not sell, trade, or otherwise transfer your personal information to third parties. 
                    We may share aggregated, anonymized data for research or service improvement purposes.
                </p>
                
                <p>We may disclose information if required by law or to:</p>
                <ul>
                    <li>Comply with legal obligations</li>
                    <li>Protect our rights and property</li>
                    <li>Prevent fraud or abuse</li>
                    <li>Ensure user safety and security</li>
                </ul>
                
                <h2>4. Data Retention</h2>
                <ul>
                    <li><strong>Rate Limiting Data:</strong> Automatically deleted after 24 hours</li>
                    <li><strong>Request Logs:</strong> Retained for debugging and analytics</li>
                    <li><strong>Error Logs:</strong> Retained for service improvement</li>
                    <li><strong>Analytics Data:</strong> Retained for trend analysis and optimization</li>
                </ul>
                
                <h2>5. Data Security</h2>
                <p>We implement appropriate security measures to protect your information:</p>
                <ul>
                    <li>Encrypted data transmission (HTTPS)</li>
                    <li>Secure database storage with access controls</li>
                    <li>Regular security updates and monitoring</li>
                    <li>Limited access to personal information</li>
                </ul>
                
                <h2>6. Your Rights</h2>
                <p>You have the right to:</p>
                <ul>
                    <li>Request information about data we collect about you</li>
                    <li>Request correction of inaccurate data</li>
                    <li>Request deletion of your data (subject to legal requirements)</li>
                    <li>Opt out of certain data collection (where technically feasible)</li>
                </ul>
                
                <h2>7. Third-Party Services</h2>
                <p>
                    Our service integrates with gaming platform APIs (Steam, Xbox, PSN, etc.) and is primarily used 
                    through the BakkesMod plugin system. These platforms and BakkesMod have their own privacy policies 
                    and data practices. We are not responsible for their privacy practices.
                </p>
                
                <div class="highlight">
                    <strong>BakkesMod Integration:</strong> When using this API through the RLProfilePicturesREVAMP 
                    BakkesMod plugin, additional data may be collected by BakkesMod itself. Please refer to 
                    BakkesMod's privacy policy for information about their data practices.
                </div>
                
                <h2>8. Children's Privacy</h2>
                <p>
                    Our service is not intended for children under 13. We do not knowingly collect 
                    personal information from children under 13. If we become aware of such collection, 
                    we will take steps to delete the information.
                </p>
                
                <h2>9. Changes to This Policy</h2>
                <p>
                    We may update this privacy policy from time to time. We will notify users of 
                    significant changes by posting the new policy on our website. Continued use of 
                    the service after changes constitutes acceptance of the updated policy.
                </p>
                
                <h2>10. BakkesMod Plugin Context</h2>
                <p>
                    This API is primarily used through the RLProfilePicturesREVAMP BakkesMod plugin, which enhances 
                    the Rocket League gaming experience by displaying user avatars within the game interface.
                </p>
                <ul>
                    <li><strong>Data Collection Context:</strong> Most data is collected during Rocket League gameplay sessions</li>
                    <li><strong>Avatar Requests:</strong> Typically triggered when viewing player profiles or match results</li>
                    <li><strong>Gaming Platforms:</strong> Data relates to avatars from platforms used by Rocket League players</li>
                    <li><strong>Real-time Processing:</strong> Optimized for low-latency responses during gameplay</li>
                </ul>
                
                <h2>11. Contact Us</h2>
                <p>
                    If you have questions about this privacy policy or our data practices, 
                    please contact us through the appropriate channels. We are committed to 
                    addressing your concerns and protecting your privacy.
                </p>
                
                <div class="footer">
                    <p>© 2025 RLProfilePicturesREVAMP API. All rights reserved.</p>
                    <p><a href="/tos">Terms of Service</a> | <a href="/">API Home</a></p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
