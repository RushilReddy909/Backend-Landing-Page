# Backend-Landing-Page

🖥️ Web Application for managing user permissions__
🔐 Allows users to update their email, phone, and address permissions__
✉️ Email, 📱 Phone, 🏠 Address - Share or revoke permissions easily__
🔄 Uses flask for backend & MongoDB for data storage__
✅ Validation for inputs and flashed messages for notifications__
💻 Admin Dashboard to manage user data and permissions__
🛠️ User-friendly interface with interactive forms and modals__

IMPORTANT__
.env file must contain the following__

FLASK_APP=app.py__
FLASK_ENV=development/production__
FLASK_DEBUG=1 (not necessary for production)__
SECRET_KEY=(some secret key, can be generated in python using 'urandom()')__
MONGO_URL=(url to the connection)__

To access the admin dashboard, please log in first. Once logged in, ensure your user role is set to 'admin' in the database. Afterward, you can visit the /admin page to view the dashboard table.__
