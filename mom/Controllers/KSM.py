# Memory Overcommitment Manager
# Copyright (C) 2010 Adam Litke, IBM Corporation
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

import logging

class KSM:
    """
    Simple controller to tune KSM paramaters.  Output triggers are:
        - ksm_run - Change the state of the KSM kernel daemon:
                        0 - Stop, 1 - Run
        - ksm_pages_to_scan - Set the number of pages to be scanned per work unit
        - ksm_sleep_millisecs - Set the time to sleep between scans
    """
    def __init__(self, properties):
        self.logger = logging.getLogger('mom.Controllers.KSM')
        self.cur = { 'run': '0', 'pages_to_scan': '0', 'sleep_millisecs': '0' }
        
    def write_value(self, fname, value):
        try:
            file = open(fname, 'w')
            file.write(str(value))
        except IOError, (errno, strerror):
            self.logger.warn("KSM: Failed to write %s: %s", fname, strerror)
        file.close()

    def process(self, host, guests):
        outputs = {}
        for key in self.cur.keys():
            rule_var =  host.GetControl('ksm_' + key)
            if rule_var is not None and rule_var != self.cur[key]:
                outputs[key] = rule_var
                self.cur[key] = rule_var

        if len(outputs) > 0:
            msg = "Updating KSM configuration: %s"
            args = []
            for (k, v) in self.cur.items():
                args.append("%s:%s" % (k,v))
            self.logger.info(msg, ' '.join(args))                
        for (key, val) in outputs.items():
            self.write_value('/sys/kernel/mm/ksm/%s' % key, val)
            self.cur[key] = val

def instance(properties):
    return KSM(properties)
