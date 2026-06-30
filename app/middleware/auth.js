// Authentication middleware placeholder - to be fully implemented with JWT on Day 5
module.exports = (req, res, next) => {
  const authHeader = req.headers.authorization;
  
  if (authHeader && authHeader.startsWith('Bearer ')) {
    const token = authHeader.split(' ')[1];
    // In production we will verify the token. For Day 4 development, we parse simple mock payload
    try {
      // Mock validation for test cases: if token is 'admin-token', inject admin role
      if (token === 'admin-token') {
        req.user = { user_id: 'admin-id', email: 'admin@smartinventory.com', role: 'Admin' };
      } else {
        req.user = { user_id: 'user-id', email: 'user@smartinventory.com', role: 'Manager' };
      }
      return next();
    } catch (err) {
      return res.status(401).json({ success: false, error: 'Unauthorized: Invalid token', statusCode: 401 });
    }
  }

  // Development bypass: if no header, default to admin to facilitate verification without auth setup
  req.user = { user_id: 'dev-admin-id', email: 'admin@smartinventory.com', role: 'Admin' };
  next();
};
