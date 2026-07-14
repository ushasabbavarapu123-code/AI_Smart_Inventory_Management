// app/tests/errorHandler.test.js

const errorHandler = require('../middleware/errorHandler');

describe('Centralized Error Handler Middleware Unit Tests', () => {
  let mockReq;
  let mockRes;
  let nextFunction;
  let consoleErrorSpy;

  beforeEach(() => {
    mockReq = {};
    mockRes = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn().mockReturnThis()
    };
    nextFunction = jest.fn();
    // Spy on console.error to suppress error output in tests
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleErrorSpy.mockRestore();
  });

  it('should use the statusCode and message provided in the error object', () => {
    const error = new Error('Database connection failed');
    error.statusCode = 503;

    errorHandler(error, mockReq, mockRes, nextFunction);

    expect(mockRes.status).toHaveBeenCalledWith(503);
    expect(mockRes.json).toHaveBeenCalledWith({
      success: false,
      error: 'Database connection failed',
      statusCode: 503
    });
    expect(consoleErrorSpy).toHaveBeenCalled();
  });

  it('should default to status code 500 and Internal Server Error message if not provided', () => {
    const error = {}; // no message or statusCode

    errorHandler(error, mockReq, mockRes, nextFunction);

    expect(mockRes.status).toHaveBeenCalledWith(500);
    expect(mockRes.json).toHaveBeenCalledWith({
      success: false,
      error: 'Internal Server Error',
      statusCode: 500
    });
  });

  it('should respect custom status codes with standard message', () => {
    const error = new Error();
    error.statusCode = 404;

    errorHandler(error, mockReq, mockRes, nextFunction);

    expect(mockRes.status).toHaveBeenCalledWith(404);
    expect(mockRes.json).toHaveBeenCalledWith({
      success: false,
      error: 'Internal Server Error', // since error has no message property, falls back to default
      statusCode: 404
    });
  });
});
