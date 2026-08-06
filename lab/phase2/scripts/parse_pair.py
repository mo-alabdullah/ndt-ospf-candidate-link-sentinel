from pathlib import Path
import json,re,sys
if len(sys.argv)!=2: raise SystemExit('Usage: parse_pair.py <measurement-directory>')
d=Path(sys.argv[1])
def parse(path):
    text=path.read_text()
    loss=re.search(r'(\d+(?:\.\d+)?)% packet loss',text)
    rtt=re.search(r'(?:rtt|round-trip) min/avg/max/(?:mdev|stddev) = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms',text)
    if not loss or not rtt: raise ValueError(f'Could not parse {path}')
    return {'packet_loss_percent':float(loss.group(1)),'rtt_min_ms':float(rtt.group(1)),'rtt_avg_ms':float(rtt.group(2)),'rtt_max_ms':float(rtt.group(3)),'rtt_variation_ms':float(rtt.group(4))}
ops=parse(d/'ops-ping.txt'); twin=parse(d/'twin-ping.txt')
summary={'operational':ops,'twin':twin,'residuals':{'rtt_avg_ms':ops['rtt_avg_ms']-twin['rtt_avg_ms'],'packet_loss_percent':ops['packet_loss_percent']-twin['packet_loss_percent']}}
(d/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
