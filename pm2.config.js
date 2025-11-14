/**
 * PM2 Process Manager Configuration for Grace
 * 
 * Install PM2: npm install -g pm2
 * 
 * Usage:
 *   pm2 start pm2.config.js
 *   pm2 stop grace
 *   pm2 restart grace
 *   pm2 logs grace
 *   pm2 monit
 */

module.exports = {
  apps: [
    {
      name: 'grace',
      script: 'serve.py',
      interpreter: 'python',
      cwd: './grace_2',
      
      // Auto-restart configuration
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      restart_delay: 5000,
      
      // Crash handling
      exp_backoff_restart_delay: 100,
      max_memory_restart: '2G',
      
      // Environment
      env: {
        PYTHONUNBUFFERED: '1',
        GRACE_ENV: 'production'
      },
      
      // Logging
      error_file: './logs/pm2_error.log',
      out_file: './logs/pm2_out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      
      // Monitoring
      instance_var: 'INSTANCE_ID',
      
      // Advanced
      listen_timeout: 10000,
      kill_timeout: 5000,
      wait_ready: true,
      
      // Ignore watch (disable auto-reload)
      watch: false,
      
      // Kill signal
      kill_signal: 'SIGTERM'
    }
  ]
};
