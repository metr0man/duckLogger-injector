import os

stat = os.statvfs('/')
free = stat[0] * stat[3]      # block_size * free_blocks
total = stat[0] * stat[2]     # block_size * total_blocks

print("Total:", total, "bytes")
print("Free :", free, "bytes")
