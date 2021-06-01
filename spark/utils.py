from datetime import datetime

log_ts = None

def reset_delta():
    global log_ts
    
    ts = datetime.now()
    log_ts = [ts, ts]
    

# Logging utils
def log(msg, delta=True):
    global log_ts
    
    curr_ts = datetime.now()
    
    # init logging
    if log_ts is None:
        reset_delta()
        out(log_ts, "Logging initialized.", delta=False)
    
    log_ts[1] = curr_ts
    out(log_ts, msg, delta=delta)
       
    # set new logging timestamps
    log_ts = [log_ts[1], datetime.now()]
    
    
def out(ts, msg, delta=True):
    fmt = None
    args = None
    
    if delta:
        fmt = '[%s | +%s s] %s'
        args = (str(ts[1]), (ts[1] - ts[0]).total_seconds(), msg)
    else:
        fmt = '[%s] %s'
        args = (str(ts[1]), msg)
        
    print(fmt % args)
    