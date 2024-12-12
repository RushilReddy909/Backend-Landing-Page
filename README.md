# Backend-Landing-Page

🖥️ Web Application for managing user permissions
🔐 Allows users to update their email, phone, and address permissions
✉️ Email, 📱 Phone, 🏠 Address - Share or revoke permissions easily
🔄 Uses flask for backend & MongoDB for data storage
✅ Validation for inputs and flashed messages for notifications
💻 Admin Dashboard to manage user data and permissions
🛠️ User-friendly interface with interactive forms and modals

IMPORTANT
.env file must contain the following

FLASK_APP=app.py
FLASK_ENV=development/production
FLASK_DEBUG=1 (not necessary for production)
SECRET_KEY=(some secret key, can be generated in python using 'urandom()')
MONGO_URL=(url to the connection)

To access the admin dashboard, please log in first. Once logged in, ensure your user role is set to 'admin' in the database. Afterward, you can visit the /admin page to view the dashboard table.
