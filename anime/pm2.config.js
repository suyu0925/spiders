module.exports = {
  apps: [{
    name: 'anime',
    script: './dist/main.js',
    watch: false,

    instances: 1,
    exec_mode: 'cluster_mode',

    // logs
    error_file: './log/error.log',
    out_file: './log/out.log',
    combine_logs: true,
    log_date_format: 'YYYY-MM-DD HH:mm:ss',

    // timeouts
    wait_ready: true,
    listen_timeout: 5000,
    kill_timeout: 3000,

    // envs
    env: {
      NODE_ENV: 'production',
    },
    env_production: {
      NODE_ENV: 'production'
    },
    env_development: {
      NODE_ENV: 'development'
    }
  }]
}
