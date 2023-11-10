#!/usr/bin/env python
# coding: utf-8

# In[20]:


import joblib
import pandas as pd
import re
import numpy as np

from sklearn.svm import LinearSVC
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import chi2, SelectPercentile
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.metrics import fbeta_score
from sklearn.model_selection import KFold

from nltk import word_tokenize		  
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import EnglishStemmer

from nltk.corpus import stopwords
import nltk


# In[21]:


nltk.download('wordnet')
nltk.download('stopwords')


# In[22]:


TEXT_FEATURES = ['processed']

CODE_TACTICS = ['TA0043', 'TA0042', 'TA0001', 'TA0002', 'TA0003', 'TA0004', 'TA0005', 'TA0006', 'TA0007', 'TA0008', 'TA0009', 'TA0011', 'TA0010', 'TA0040']
NAME_TACTICS = ['Reconnaissance', 'Resource Development', 'Initial Access', 'Execution', 'Persistence', 'Privilege Escalation', 'Defense Evasion', 'Credential Access', 'Discovery', 'Lateral Movement', 'Collection', 'Command and Control', 'Exfiltration', 'Impact']

CODE_TECHNIQUES = ['T1595', 'T1592', 'T1589', 'T1590', 'T1591', 'T1598', 'T1597', 'T1596', 'T1593', 'T1594', 'T1583', 'T1586', 'T1584', 'T1587', 'T1585', 'T1588', 'T1608', 'T1189', 'T1190', 'T1133', 'T1200', 'T1566', 'T1091', 'T1195', 'T1199', 'T1078', 'T1059', 'T1609', 'T1610', 'T1203', 'T1559', 'T1106', 'T1053', 'T1129', 'T1072', 'T1569', 'T1204', 'T1047', 'T1098', 'T1197', 'T1547', 'T1037', 'T1176', 'T1554', 'T1136', 'T1543', 'T1546', 'T1574', 'T1525', 'T1556', 'T1137', 'T1542', 'T1505', 'T1205', 'T1548', 'T1134', 'T1484', 'T1611', 'T1068', 'T1055', 'T1612', 'T1622', 'T1140', 'T1006', 'T1480', 'T1211', 'T1222', 'T1564', 'T1562', 'T1070', 'T1202', 'T1036', 'T1578', 'T1112', 'T1601', 'T1599', 'T1027', 'T1647', 'T1620', 'T1207', 'T1014', 'T1553', 'T1218', 'T1216', 'T1221', 'T1127', 'T1535', 'T1550', 'T1497', 'T1600', 'T1220', 'T1557', 'T1110', 'T1555', 'T1212', 'T1187', 'T1606', 'T1056', 'T1111', 'T1621', 'T1040', 'T1003', 'T1528', 'T1558', 'T1539', 'T1552', 'T1087', 'T1010', 'T1217', 'T1580', 'T1538', 'T1526', 'T1619', 'T1613', 'T1482', 'T1083', 'T1615', 'T1046', 'T1135', 'T1201', 'T1120', 'T1069', 'T1057', 'T1012', 'T1018', 'T1518', 'T1082', 'T1614', 'T1016', 'T1049', 'T1033', 'T1007', 'T1124', 'T1210', 'T1534', 'T1570', 'T1563', 'T1021', 'T1080', 'T1560', 'T1123', 'T1119', 'T1185', 'T1115', 'T1530', 'T1602', 'T1213', 'T1005', 'T1039', 'T1025', 'T1074', 'T1114', 'T1113', 'T1125', 'T1071', 'T1092', 'T1132', 'T1001', 'T1568', 'T1573', 'T1008', 'T1105', 'T1104', 'T1095', 'T1571', 'T1572', 'T1090', 'T1219', 'T1102', 'T1020', 'T1030', 'T1048', 'T1041', 'T1011', 'T1052', 'T1567', 'T1029', 'T1537', 'T1531', 'T1485', 'T1486', 'T1565', 'T1491', 'T1561', 'T1499', 'T1495', 'T1490', 'T1498', 'T1496', 'T1489', 'T1529']
NAME_TECHNIQUES = ['Active Scanning', 'Gather Victim Host Information', 'Gather Victim Identity Information', 'Gather Victim Network Information', 'Gather Victim Org Information', 'Phishing for Information', 'Search Closed Sources', 'Search Open Technical Databases', 'Search Open Websites/Domains', 'Search Victim-Owned Websites', 'Acquire Infrastructure', 'Compromise Accounts', 'Compromise Infrastructure', 'Develop Capabilities', 'Establish Accounts', 'Obtain Capabilities', 'Stage Capabilities', 'Drive-by Compromise', 'Exploit Public-Facing Application', 'External Remote Services', 'Hardware Additions', 'Phishing', 'Replication Through Removable Media', 'Supply Chain Compromise', 'Trusted Relationship', 'Valid Accounts', 'Command and Scripting Interpreter', 'Container Administration Command', 'Deploy Container', 'Exploitation for Client Execution', 'Inter-Process Communication', 'Native API', 'Scheduled Task/Job', 'Shared Modules', 'Software Deployment Tools', 'System Services', 'User Execution', 'Windows Management Instrumentation', 'Account Manipulation', 'BITS Jobs', 'Boot or Logon Autostart Execution', 'Boot or Logon Initialization Scripts', 'Browser Extensions', 'Compromise Client Software Binary', 'Create Account', 'Create or Modify System Process', 'Event Triggered Execution', 'Hijack Execution Flow', 'Implant Internal Image', 'Modify Authentication Process', 'Office Application Startup', 'Pre-OS Boot', 'Server Software Component', 'Traffic Signaling', 'Abuse Elevation Control Mechanism', 'Access Token Manipulation', 'Domain Policy Modification', 'Escape to Host', 'Exploitation for Privilege Escalation', 'Process Injection', 'Build Image on Host', 'Debugger Evasion', 'Deobfuscate/Decode Files or Information', 'Direct Volume Access', 'Execution Guardrails', 'Exploitation for Defense Evasion', 'File and Directory Permissions Modification', 'Hide Artifacts', 'Impair Defenses', 'Indicator Removal on Host', 'Indirect Command Execution', 'Masquerading', 'Modify Cloud Compute Infrastructure', 'Modify Registry', 'Modify System Image', 'Network Boundary Bridging', 'Obfuscated Files or Information', 'Plist File Modification', 'Reflective Code Loading', 'Rogue Domain Controller', 'Rootkit', 'Subvert Trust Controls', 'Signed Binary Proxy Execution', 'Signed Script Proxy Execution', 'Template Injection', 'Trusted Developer Utilities Proxy Execution', 'Unused/Unsupported Cloud Regions', 'Use Alternate Authentication Material', 'Virtualization/Sandbox Evasion', 'Weaken Encryption', 'XSL Script Processing', 'Adversary-in-the-Middle', 'Brute Force', 'Credentials from Password Stores', 'Exploitation for Credential Access', 'Forced Authentication', 'Forge Web Credentials', 'Input Capture', 'Two-Factor Authentication Interception', 'Multi-Factor Authentication Request Generation', 'Network Sniffing', 'OS Credential Dumping', 'Steal Application Access Token', 'Steal or Forge Kerberos Tickets', 'Steal Web Session Cookie', 'Unsecured Credentials', 'Account Discovery', 'Application Window Discovery', 'Browser Bookmark Discovery', 'Cloud Infrastructure Discovery', 'Cloud Service Dashboard', 'Cloud Service Discovery', 'Cloud Storage Object Discovery', 'Container and Resource Discovery', 'Domain Trust Discovery', 'File and Directory Discovery', 'Group Policy Discovery', 'Network Service Scanning', 'Network Share Discovery', 'Password Policy Discovery', 'Peripheral Device Discovery', 'Permission Groups Discovery', 'Process Discovery', 'Query Registry', 'Remote System Discovery', 'Software Discovery', 'System Information Discovery', 'System Location Discovery', 'System Network Configuration Discovery', 'System Network Connections Discovery', 'System Owner/User Discovery', 'System Service Discovery', 'System Time Discovery', 'Exploitation of Remote Services', 'Internal Spearphishing', 'Lateral Tool Transfer', 'Remote Service Session Hijacking', 'Remote Services', 'Taint Shared Content', 'Archive Collected Data', 'Audio Capture', 'Automated Collection', 'Browser Session Hijacking', 'Clipboard Data', 'Data from Cloud Storage Object', 'Data from Configuration Repository', 'Data from Information Repositories', 'Data from Local System', 'Data from Network Shared Drive', 'Data from Removable Media', 'Data Staged', 'Email Collection', 'Screen Capture', 'Video Capture', 'Application Layer Protocol', 'Communication Through Removable Media', 'Data Encoding', 'Data Obfuscation', 'Dynamic Resolution', 'Encrypted Channel', 'Fallback Channels', 'Ingress Tool Transfer', 'Multi-Stage Channels', 'Non-Application Layer Protocol', 'Non-Standard Port', 'Protocol Tunneling', 'Proxy', 'Remote Access Software', 'Web Service', 'Automated Exfiltration', 'Data Transfer Size Limits', 'Exfiltration Over Alternative Protocol', 'Exfiltration Over C2 Channel', 'Exfiltration Over Other Network Medium', 'Exfiltration Over Physical Medium', 'Exfiltration Over Web Service', 'Scheduled Transfer', 'Transfer Data to Cloud Account', 'Account Access Removal', 'Data Destruction', 'Data Encrypted for Impact', 'Data Manipulation', 'Defacement', 'Disk Wipe', 'Endpoint Denial of Service', 'Firmware Corruption', 'Inhibit System Recovery', 'Network Denial of Service', 'Resource Hijacking', 'Service Stop', 'System Shutdown/Reboot']

ALL_TTPS = ['TA0043', 'TA0042', 'TA0001', 'TA0002', 'TA0003', 'TA0004', 'TA0005', 'TA0006', 'TA0007', 'TA0008', 'TA0009', 'TA0011', 'TA0010', 'TA0040', 'T1595', 'T1592', 'T1589', 'T1590', 'T1591', 'T1598', 'T1597', 'T1596', 'T1593', 'T1594', 'T1583', 'T1586', 'T1584', 'T1587', 'T1585', 'T1588', 'T1608', 'T1189', 'T1190', 'T1133', 'T1200', 'T1566', 'T1091', 'T1195', 'T1199', 'T1078', 'T1059', 'T1609', 'T1610', 'T1203', 'T1559', 'T1106', 'T1053', 'T1129', 'T1072', 'T1569', 'T1204', 'T1047', 'T1098', 'T1197', 'T1547', 'T1037', 'T1176', 'T1554', 'T1136', 'T1543', 'T1546', 'T1574', 'T1525', 'T1556', 'T1137', 'T1542', 'T1505', 'T1205', 'T1548', 'T1134', 'T1484', 'T1611', 'T1068', 'T1055', 'T1612', 'T1622', 'T1140', 'T1006', 'T1480', 'T1211', 'T1222', 'T1564', 'T1562', 'T1070', 'T1202', 'T1036', 'T1578', 'T1112', 'T1601', 'T1599', 'T1027', 'T1647', 'T1620', 'T1207', 'T1014', 'T1553', 'T1218', 'T1216', 'T1221', 'T1127', 'T1535', 'T1550', 'T1497', 'T1600', 'T1220', 'T1557', 'T1110', 'T1555', 'T1212', 'T1187', 'T1606', 'T1056', 'T1111', 'T1621', 'T1040', 'T1003', 'T1528', 'T1558', 'T1539', 'T1552', 'T1087', 'T1010', 'T1217', 'T1580', 'T1538', 'T1526', 'T1619', 'T1613', 'T1482', 'T1083', 'T1615', 'T1046', 'T1135', 'T1201', 'T1120', 'T1069', 'T1057', 'T1012', 'T1018', 'T1518', 'T1082', 'T1614', 'T1016', 'T1049', 'T1033', 'T1007', 'T1124', 'T1210', 'T1534', 'T1570', 'T1563', 'T1021', 'T1080', 'T1560', 'T1123', 'T1119', 'T1185', 'T1115', 'T1530', 'T1602', 'T1213', 'T1005', 'T1039', 'T1025', 'T1074', 'T1114', 'T1113', 'T1125', 'T1071', 'T1092', 'T1132', 'T1001', 'T1568', 'T1573', 'T1008', 'T1105', 'T1104', 'T1095', 'T1571', 'T1572', 'T1090', 'T1219', 'T1102', 'T1020', 'T1030', 'T1048', 'T1041', 'T1011', 'T1052', 'T1567', 'T1029', 'T1537', 'T1531', 'T1485', 'T1486', 'T1565', 'T1491', 'T1561', 'T1499', 'T1495', 'T1490', 'T1498', 'T1496', 'T1489', 'T1529']
STIX_IDENTIFIERS = ['x-mitre-tactic--daa4cbb1-b4f4-4723-a824-7f1efd6e0592', 'x-mitre-tactic--d679bca2-e57d-4935-8650-8031c87a4400', 'x-mitre-tactic--ffd5bcee-6e16-4dd2-8eca-7b3beedf33ca', 'x-mitre-tactic--4ca45d45-df4d-4613-8980-bac22d278fa5', 'x-mitre-tactic--5bc1d813-693e-4823-9961-abf9af4b0e92', 'x-mitre-tactic--5e29b093-294e-49e9-a803-dab3d73b77dd', 'x-mitre-tactic--78b23412-0651-46d7-a540-170a1ce8bd5a', 'x-mitre-tactic--2558fd61-8c75-4730-94c4-11926db2a263', 'x-mitre-tactic--c17c5845-175e-4421-9713-829d0573dbc9', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--d108ce10-2419-4cf9-a774-46161d6c6cfe', 'x-mitre-tactic--f72804c5-f15a-449e-a5da-2eecd181f813', 'x-mitre-tactic--9a4e74ab-5008-408c-84bf-a10dfbc53462', 'x-mitre-tactic--5569339b-94c2-49ee-afb3-2222936582c8', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e', 'x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e']

TACTICS_TECHNIQUES_RELATIONSHIP_DF = pd.DataFrame({'TA0043': pd.Series(['T1595', 'T1592', 'T1589', 'T1590', 'T1591', 'T1598', 'T1597', 'T1596', 'T1593', 'T1594']),
                                        'TA0042': pd.Series(['T1583', 'T1586', 'T1584', 'T1587', 'T1585', 'T1588', 'T1608']),
                                        'TA0001': pd.Series(['T1189', 'T1190', 'T1133', 'T1200', 'T1566', 'T1091', 'T1195', 'T1199', 'T1078']),
                                        'TA0002': pd.Series(['T1059', 'T1609', 'T1610', 'T1203', 'T1559', 'T1106', 'T1053', 'T1129', 'T1072', 'T1569', 'T1204', 'T1047']),
                                        'TA0003': pd.Series(['T1098', 'T1197', 'T1547', 'T1037', 'T1176', 'T1554', 'T1136', 'T1543', 'T1546', 'T1133', 'T1574', 'T1525', 'T1556', 'T1137', 'T1542', 'T1053', 'T1505', 'T1205', 'T1078']),
                                        'TA0004': pd.Series(['T1548', 'T1134', 'T1547', 'T1037', 'T1543', 'T1484', 'T1611', 'T1546', 'T1068', 'T1574', 'T1055', 'T1053', 'T1078']),
                                        'TA0005': pd.Series(['T1548', 'T1134', 'T1197', 'T1612', 'T1622', 'T1140', 'T1610', 'T1006', 'T1484', 'T1480', 'T1211', 'T1222', 'T1564', 'T1574', 'T1562', 'T1070', 'T1202', 'T1036', 'T1556', 'T1578', 'T1112', 'T1601', 'T1599', 'T1027', 'T1647', 'T1542', 'T1055', 'T1620', 'T1207', 'T1014', 'T1553', 'T1218', 'T1216', 'T1221', 'T1205', 'T1127', 'T1535', 'T1550', 'T1078', 'T1497', 'T1600', 'T1220']),
                                        'TA0006': pd.Series(['T1557', 'T1110', 'T1555', 'T1212', 'T1187', 'T1606', 'T1056', 'T1556', 'T1111', 'T1621', 'T1040', 'T1003', 'T1528', 'T1558', 'T1539', 'T1552']),
                                        'TA0007': pd.Series(['T1087', 'T1010', 'T1217', 'T1580', 'T1538', 'T1526', 'T1619', 'T1613', 'T1622', 'T1482', 'T1083', 'T1615', 'T1046', 'T1135', 'T1040', 'T1201', 'T1120', 'T1069', 'T1057', 'T1012', 'T1018', 'T1518', 'T1082', 'T1614', 'T1016', 'T1049', 'T1033', 'T1007', 'T1124', 'T1497']),
                                        'TA0008': pd.Series(['T1210', 'T1534', 'T1570', 'T1563', 'T1021', 'T1091', 'T1072', 'T1080', 'T1550']),
                                        'TA0009': pd.Series(['T1557', 'T1560', 'T1123', 'T1119', 'T1185', 'T1115', 'T1530', 'T1602', 'T1213', 'T1005', 'T1039', 'T1025', 'T1074', 'T1114', 'T1056', 'T1113', 'T1125']),
                                        'TA0011': pd.Series(['T1071', 'T1092', 'T1132', 'T1001', 'T1568', 'T1573', 'T1008', 'T1105', 'T1104', 'T1095', 'T1571', 'T1572', 'T1090', 'T1219', 'T1205', 'T1102']),
                                        'TA0010': pd.Series(['T1020', 'T1030', 'T1048', 'T1041', 'T1011', 'T1052', 'T1567', 'T1029', 'T1537']),
                                        'TA0040': pd.Series(['T1531', 'T1485', 'T1486', 'T1565', 'T1491', 'T1561', 'T1499', 'T1495', 'T1490', 'T1498', 'T1496', 'T1489', 'T1529'])
                                        })


# In[23]:


def clean_text(text):
	"""
	Cleaning up the words contractions, unusual spacing, non-word characters and any computer science
	related terms that hinder the classification.
	"""
	text = str(text)
	text = text.lower()
	text = re.sub("\r\n", "\t", text)
	text = re.sub(r"what's", "what is ", text)
	text = re.sub(r"\'s", " ", text)
	text = re.sub(r"\'ve", " have ", text)
	text = re.sub(r"can't", "can not ", text)
	text = re.sub(r"n't", " not ", text)
	text = re.sub(r"i'm", "i am ", text)
	text = re.sub(r"\'re", " are ", text)
	text = re.sub(r"\'d", " would ", text)
	text = re.sub(r"\'ll", " will ", text)
	text = re.sub(r"\'scuse", " excuse ", text)
	text = re.sub('(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.)\{3\}(?:25[0-5] |2[0-4][0-9]|[01]?[0-9][0-9]?)(/([0-2][0-9]|3[0-2]|[0-9]))?', 'IPv4', text)
	text = re.sub('\b(CVE\-[0-9]{4}\-[0-9]{4,6})\b', 'CVE', text)
	text = re.sub('\b([a-z][_a-z0-9-.]+@[a-z0-9-]+\.[a-z]+)\b', 'email', text)
	text = re.sub('\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b', 'IP', text)
	text = re.sub('\b([a-f0-9]{32}|[A-F0-9]{32})\b', 'MD5', text)
	text = re.sub('\b((HKLM|HKCU)\\[\\A-Za-z0-9-_]+)\b', 'registry', text)
	text = re.sub('\b([a-f0-9]{40}|[A-F0-9]{40})\b', 'SHA1', text)
	text = re.sub('\b([a-f0-9]{64}|[A-F0-9]{64})\b', 'SHA250', text)
	text = re.sub('http(s)?:\\[0-9a-zA-Z_\.\-\\]+.', 'URL', text)
	text = re.sub('CVE-[0-9]{4}-[0-9]{4,6}', 'vulnerability', text)
	text = re.sub('[a-zA-Z]{1}:\\[0-9a-zA-Z_\.\-\\]+', 'file', text)
	text = re.sub('\b[a-fA-F\d]{32}\b|\b[a-fA-F\d]{40}\b|\b[a-fA-F\d]{64}\b', 'hash', text)
	text = re.sub('x[A-Fa-f0-9]{2}', ' ', text)
	text = re.sub('\W', ' ', text)
	text = re.sub('\s+', ' ', text)
	text = text.strip(' ')
	return text

def processing(df):
	"""
	Creating a function to encapsulate preprocessing, to make it easy to replicate on submission data
	"""
	df['processed'] = df['Text'].map(lambda com : clean_text(com))
	return(df)

def remove_u(input_string):
	"""
	Convert unicode text
	"""
	words = input_string.split()
	words_u = [(word.encode('unicode-escape')).decode("utf-8", "strict") for word in words]
	words_u = [word_u.split('\\u')[1] if r'\u' in word_u else word_u for word_u in words_u]
	return ' '.join(words_u)

class StemTokenizer(object):
	"""
	Transform each word to its stemmed version
	e.g. studies --> studi
	"""
	def __init__(self):
		self.st = EnglishStemmer()
		
	def __call__(self, doc):
		return [self.st.stem(t) for t in word_tokenize(doc)]

class LemmaTokenizer(object):
	"""
	Transform each word to its lemmatized version
	e.g. studies --> study
	"""
	def __init__(self):
		self.wnl = WordNetLemmatizer()
		
	def __call__(self, doc):
		return [self.wnl.lemmatize(t) for t in word_tokenize(doc)]

class TextSelector(BaseEstimator, TransformerMixin):
	"""
	Transformer to select a single column from the data frame to perform additional transformations on
	Use on text columns in the data
	"""
	def __init__(self, key):
		self.key = key

	def fit(self, X, y=None):
		return self

	def transform(self, X):
		return X[self.key]


# In[24]:


def print_progress_bar(iteration):
	"""
	Print a progress bar for command-line interface training
	"""
	percent = ("{0:.1f}").format(100 * (iteration / float(50)))
	filledLength = int(iteration)
	bar = '█' * filledLength + '-' * (50 - filledLength)
	prefix = "Progress:"
	suffix = "Complete"
	printEnd = "\r"
	print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
	if iteration == 50: 
		print()

def confidence_propagation_single(tactics_confidence_list, technique_name, technique_confidence_score):
	"""
	Modify predictions and confidence scores of one technique  using a boosting method depending on this
	technique's and its related tactics' confidence score.
	"""
	new_confidence_score = technique_confidence_score
	i = 0
	for tactic in CODE_TACTICS:
		if not TACTICS_TECHNIQUES_RELATIONSHIP_DF.loc[TACTICS_TECHNIQUES_RELATIONSHIP_DF[tactic] == technique_name].empty:
			lambdaim = 1/(np.exp(abs(technique_confidence_score-tactics_confidence_list[tactic])))
			new_confidence_score = new_confidence_score + lambdaim * tactics_confidence_list[tactic]
		i = i+1
	return new_confidence_score

def confidence_propagation( predprob_tactics, pred_techniques, predprob_techniques):
	"""
	Modify predictions and confidences scores of all techniques of the whole set using 
	confidence_propagation_single function.
	"""
	pred_techniques_corrected = pred_techniques
	predprob_techniques_corrected = predprob_techniques
	tactics_confidence_df = pd.DataFrame(data = predprob_tactics, columns = CODE_TACTICS)
	for j in range(len(predprob_techniques[0])):
		for i in range(len(predprob_techniques)):
			predprob_techniques_corrected[i][j] = confidence_propagation_single(tactics_confidence_df[i:(i+1)], CODE_TECHNIQUES[j], predprob_techniques[i][j])
			if predprob_techniques_corrected[i][j] >= float(0) :
				pred_techniques_corrected[i][j] = int(1)
			else:
				pred_techniques_corrected[i][j] = int(0)
	return pred_techniques_corrected, predprob_techniques_corrected

def hanging_node(pred_tactics, predprob_tactics, pred_techniques, predprob_techniques, c, d):
	"""
	Modify prediction of techniques depending on techniques and related tactics confidence score on a
	threshold basis.
	"""
	predprob_techniques_corrected = pred_techniques
	for i in range(len(pred_techniques)):
		for j in range(len(pred_techniques[0])):
			for k in range(len(pred_tactics[0])):
				if not TACTICS_TECHNIQUES_RELATIONSHIP_DF.loc[TACTICS_TECHNIQUES_RELATIONSHIP_DF[CODE_TACTICS[k]] == CODE_TECHNIQUES[j]].empty:
					if predprob_techniques[i][j] < c and predprob_techniques[i][j] > 0 and predprob_tactics[i][k] < d:
						predprob_techniques_corrected[i][k] = 0 
	return predprob_techniques_corrected

def combinations(c, d):
	"""
	Compute all combinations possible between c and d and their derived values.
	"""
	c_list = [c-0.1, c, c+0.1]
	d_list = [d-0.1, d, d+0.1]
	possibilities = []
	for cl in c_list:
		for dl in d_list:
			possibilities.append([cl, dl])
	return possibilities

def hanging_node_threshold_comparison(pred_tactics, predprob_tactics, pred_techniques, predprob_techniques, known_pred_techniques, permutations):
	"""
	Using different combinations of thresholds retrieve all the F0.5 score macro-averaged between the
	post-processed predictions and the true labels.
	"""
	f05list = []
	for pl in permutations:
		f05list_temp = [pl]
		new_pred_techniques = hanging_node(pred_tactics, predprob_tactics, pred_techniques, predprob_techniques, pl[0], pl[1])
		f05list_temp.append(fbeta_score(known_pred_techniques, new_pred_techniques, beta=0.5, average='macro'))
		f05list.append(f05list_temp)
	return f05list

def find_best_post_processing(cmd):
	"""
	Find best postprocessing approach to use with the new dataset based on the f0.5 score macro-averaged.
	"""
	# add stop words to the list found during the development of rcATT
	stop_words = stopwords.words('english')
	new_stop_words = ["'ll", "'re", "'ve", 'ha', 'wa',"'d", "'s", 'abov', 'ani', 'becaus', 'befor', 'could', 'doe', 'dure', 'might', 'must', "n't", 'need', 'onc', 'onli', 'ourselv', 'sha', 'themselv', 'veri', 'whi', 'wo', 'would', 'yourselv']
	stop_words.extend(new_stop_words)
	
	train_data_df = pd.read_csv('Dataset.csv', encoding = "ISO-8859-1")
	
	# preprocess the report
	train_data_df = processing(train_data_df)
	
	# split the dataset in 5 fold to be able to give a more accurate F0.5 score
	kf = KFold(n_splits=5, shuffle = True, random_state=42)
	reports = train_data_df[TEXT_FEATURES]
	overall_ttps = train_data_df[ALL_TTPS]
	
	# get current configuration parameters for post-processing method hanging-node to define new thresholds
	parameters = joblib.load("Models/configuration.joblib")
	c = parameters[1][0]
	d = parameters[1][1]
	permutations = combinations(c, d)
	
	f05_NO = [] #list of f0.5 score for all techniques predictions sets without post-processing
	f05_HN = [] #list of f0.5 score for all techniques predictions sets with hanging node post-processing
	f05_CP = [] #list of f0.5 score for all techniques predictions sets with confidence propagation post-processing
	
	# retrieve minimum and maximum probabilities to use in MinMaxScaler
	min_prob_tactics = 0.0
	max_prob_tactics = 0.0
	min_prob_techniques = 0.0
	max_prob_techniques = 0.0
	
	i = 6 # print progress bar counter
	
	for index1, index2 in kf.split(reports, overall_ttps):
		# splits the dataset according to the kfold split into training and testing sets, and data and labels
		reports_train, reports_test = reports.iloc[index1], reports.iloc[index2]
		overall_ttps_train, overall_ttps_test = overall_ttps.iloc[index1], overall_ttps.iloc[index2]

		train_reports = reports_train[TEXT_FEATURES]
		test_reports = reports_test[TEXT_FEATURES]

		train_tactics = overall_ttps_train[CODE_TACTICS]
		train_techniques = overall_ttps_train[CODE_TECHNIQUES]
		test_tactics = overall_ttps_test[CODE_TACTICS]
		test_techniques = overall_ttps_test[CODE_TECHNIQUES]
		
		# Define a pipeline combining a text feature extractor with multi label classifier for the tactics predictions
		pipeline_tactics = Pipeline([
				('columnselector', TextSelector(key = 'processed')),
				('tfidf', TfidfVectorizer(tokenizer = LemmaTokenizer(), stop_words = stop_words, max_df = 0.90)),
				('selection', SelectPercentile(chi2, percentile = 50)),
				('classifier', OneVsRestClassifier(LinearSVC(penalty = 'l2', loss = 'squared_hinge', dual = True, class_weight = 'balanced'), n_jobs = 1))
			])
		# train the model and predict the tactics
		pipeline_tactics.fit(train_reports, train_tactics)
		pred_tactics = pipeline_tactics.predict(test_reports)
		predprob_tactics = pipeline_tactics.decision_function(test_reports)
		
		if np.amin(predprob_tactics) < min_prob_tactics:
			min_prob_tactics = np.amin(predprob_tactics)
		if np.amax(predprob_tactics) > max_prob_tactics:
			max_prob_tactics = np.amax(predprob_tactics)
		
		if cmd:
			print_progress_bar(i)
		
		# Define a pipeline combining a text feature extractor with multi label classifier for the techniques predictions
		pipeline_techniques = Pipeline([
				('columnselector', TextSelector(key = 'processed')),
				('tfidf', TfidfVectorizer(tokenizer = StemTokenizer(), stop_words = stop_words, min_df = 2, max_df = 0.99)),
				('selection', SelectPercentile(chi2, percentile = 50)),
				('classifier', OneVsRestClassifier(LinearSVC(penalty = 'l2', loss = 'squared_hinge', dual = False, max_iter = 1000, class_weight = 'balanced'), n_jobs = 1))
			])
		# train the model and predict the techniques
		pipeline_techniques.fit(train_reports, train_techniques)
		pred_techniques = pipeline_techniques.predict(test_reports)
		predprob_techniques = pipeline_techniques.decision_function(test_reports)
		
		if np.amin(predprob_techniques) < min_prob_techniques:
			min_prob_techniques = np.amin(predprob_techniques)
		if np.amax(predprob_techniques) > max_prob_techniques:
			max_prob_techniques = np.amax(predprob_techniques)
		
		i+=2
		if cmd:
			print_progress_bar(i)
		
		# calculate the F0.5 score for each type of post processing and append to the list to keep track over the different folds
		f05_NO.append(fbeta_score(test_techniques, pred_techniques, beta = 0.5, average = 'macro'))
		f05_HN.extend(hanging_node_threshold_comparison(pred_tactics, predprob_tactics, pred_techniques, predprob_techniques, test_techniques, permutations))
		
		i+=2
		if cmd:
			print_progress_bar(i)
		
		CPres, _ = confidence_propagation(predprob_tactics, pred_techniques, predprob_techniques)
		
		i+=2
		if cmd:
			print_progress_bar(i)
		
		f05_CP.append(fbeta_score(test_techniques, CPres, beta = 0.5, average = 'macro'))
		
		i+=2
	
	save_post_processing_comparison=[]
	# find the F0.5 average for each post-processing
	fb05_NO_avg = np.mean(f05_NO)
	fb05_CP_avg = np.mean(f05_CP)
	best_HN=[]
	fb05_Max_HN_avg = 0
	
	if cmd:
		print_progress_bar(48)

	for ps in permutations:
		sum = []
		for prhn in f05_HN:
			if ps == prhn[0]:
				sum.append(prhn[1])
		avg_temp = np.mean(sum)
		if avg_temp >= fb05_Max_HN_avg:
			fb05_Max_HN_avg = avg_temp
			best_HN = ps

	# define the best post-processing based on the F0.5 score average
	if fb05_NO_avg >= fb05_CP_avg and fb05_NO_avg >= fb05_Max_HN_avg:
		save_post_processing_comparison = ["N"]
	elif fb05_CP_avg >= fb05_Max_HN_avg and fb05_CP_avg >= fb05_NO_avg:
		save_post_processing_comparison = ["CP"]
	else:
		save_post_processing_comparison = ["HN"]
	save_post_processing_comparison.extend([best_HN, [min_prob_tactics, max_prob_tactics], [min_prob_techniques, max_prob_techniques]])
	
	# save the results
	joblib.dump(save_post_processing_comparison, "Models/configuration.joblib")
	
	if cmd:
		print_progress_bar(50)
		print()


# In[25]:


def train(cmd):
	"""
	Train again rcATT with a new dataset
	"""
	
	# stopwords with additional words found during the development
	stop_words = stopwords.words('english')
	new_stop_words = ["'ll", "'re", "'ve", 'ha', 'wa',"'d", "'s", 'abov', 'ani', 'becaus', 'befor', 'could', 'doe', 'dure', 'might', 'must', "n't", 'need', 'onc', 'onli', 'ourselv', 'sha', 'themselv', 'veri', 'whi', 'wo', 'would', 'yourselv']
	stop_words.extend(new_stop_words)
	
	# load all possible data
	train_data_df = pd.read_csv('Dataset.csv', encoding = "ISO-8859-1")

	train_data_df = processing(train_data_df)

	reports = train_data_df[TEXT_FEATURES]
	tactics = train_data_df[CODE_TACTICS]
	techniques = train_data_df[CODE_TECHNIQUES]
	
	if cmd:
		print_progress_bar(0)
	
	# Define a pipeline combining a text feature extractor with multi label classifier for tactics prediction
	pipeline_tactics = Pipeline([
			('columnselector', TextSelector(key = 'processed')),
			('tfidf', TfidfVectorizer(tokenizer = LemmaTokenizer(), stop_words = stop_words, max_df = 0.90)),
			('selection', SelectPercentile(chi2, percentile = 50)),
			('classifier', OneVsRestClassifier(LinearSVC(penalty = 'l2', loss = 'squared_hinge', dual = True, class_weight = 'balanced'), n_jobs = 1))
		])
	
	# train the model for tactics
	pipeline_tactics.fit(reports, tactics)
	
	if cmd:
		print_progress_bar(2)
	
	# Define a pipeline combining a text feature extractor with multi label classifier for techniques prediction
	pipeline_techniques = Pipeline([
			('columnselector', TextSelector(key = 'processed')),
			('tfidf', TfidfVectorizer(tokenizer = StemTokenizer(), stop_words = stop_words, min_df = 2, max_df = 0.99)),
			('selection', SelectPercentile(chi2, percentile = 50)),
			('classifier', OneVsRestClassifier(LinearSVC(penalty = 'l2', loss = 'squared_hinge', dual = False, max_iter = 1000, class_weight = 'balanced'), n_jobs = 1))
		])
	
	# train the model for techniques
	pipeline_techniques.fit(reports, techniques)
	
	if cmd:
		print_progress_bar(4)
	
	find_best_post_processing(cmd)
	
	#Save model
	joblib.dump(pipeline_tactics, 'Models/tactics.joblib')
	joblib.dump(pipeline_techniques, 'Models/techniques.joblib')


# In[26]:


train(True)


# In[27]:


def predict_new(report_to_predict, post_processing_parameters):
	"""
	Predict tactics and techniques from a report in a txt file.
	"""

	# loading the models
	pipeline_tactics = joblib.load('Models/tactics.joblib')
	pipeline_techniques = joblib.load('Models/techniques.joblib')

	report = processing(pd.DataFrame([report_to_predict], columns = ['Text']))[TEXT_FEATURES]
	
	# predictions
	predprob_tactics = pipeline_tactics.decision_function(report)
	pred_tactics = pipeline_tactics.predict(report)

	predprob_techniques = pipeline_techniques.decision_function(report)
	pred_techniques = pipeline_techniques.predict(report)
	
	if post_processing_parameters[0] == "HN":
		# hanging node thresholds retrieval and hanging node performed on predictions if in parameters
		pred_techniques = hanging_node(pred_tactics, predprob_tactics, pred_techniques, predprob_techniques, post_processing_parameters[1][0], post_processing_parameters[1][1])
	elif post_processing_parameters[0] == "CP":
		# confidence propagation performed on prediction if in parameters
		pred_techniques, predprob_techniques = confidence_propagation(predprob_tactics, pred_techniques, predprob_techniques)

	i = 0
	
	return pred_tactics, predprob_tactics, pred_techniques, predprob_techniques


# In[28]:


OLD_CODE_TACTICS = ["TA0006","TA0002","TA0040","TA0003","TA0004","TA0008","TA0005","TA0010","TA0007","TA0009","TA0011","TA0001"]
OLD_NAME_TACTICS = ["Credential Access","Execution","Impact","Persistence","Privilege Escalation","Lateral Movement","Defense Evasion","Exfiltration","Discovery","Collection","Command and Control","Initial Access"]
OLD_CODE_TECHNIQUES = ["T1066","T1047","T1156","T1113","T1067","T1037","T1033","T1003","T1129","T1492","T1044","T1171","T1014","T1501","T1123","T1133","T1109","T1099","T1069","T1114","T1163","T1025","T1116","T1093","T1178","T1013","T1192","T1489","T1206","T1063","T1080","T1167","T1165","T1137","T1089","T1487","T1214","T1119","T1115","T1103","T1007","T1040","T1135","T1120","T1082","T1071","T1053","T1162","T1176","T1106","T1058","T1202","T1024","T1091","T1005","T1140","T1195","T1190","T1219","T1079","T1036","T1055","T1205","T1218","T1038","T1050","T1010","T1032","T1062","T1182","T1029","T1004","T1009","T1076","T1131","T1181","T1483","T1185","T1021","T1207","T1107","T1145","T1112","T1491","T1155","T1217","T1183","T1085","T1031","T1092","T1222","T1179","T1019","T1042","T1117","T1054","T1108","T1193","T1215","T1101","T1177","T1125","T1144","T1045","T1016","T1198","T1087","T1090","T1059","T1482","T1175","T1020","T1070","T1083","T1138","T1191","T1188","T1074","T1049","T1064","T1051","T1497","T1102","T1104","T1480","T1204","T1196","T1057","T1141","T1041","T1060","T1023","T1026","T1122","T1015","T1212","T1210","T1142","T1199","T1098","T1170","T1048","T1097","T1110","T1001","T1039","T1078","T1073","T1068","T1208","T1027","T1201","T1187","T1486","T1488","T1174","T1002","T1081","T1128","T1056","T1203","T1168","T1100","T1186","T1184","T1095","T1075","T1012","T1030","T1028","T1034","T1499","T1065","T1197","T1088","T1493","T1132","T1500","T1223","T1213","T1194","T1200","T1485","T1130","T1022","T1189","T1498","T1158","T1221","T1134","T1209","T1111","T1159","T1136","T1018","T1046","T1052","T1105","T1084","T1160","T1484","T1220","T1173","T1008","T1096","T1124","T1035","T1086","T1490","T1216","T1094","T1043","T1211","T1127","T1077"]
OLD_NAME_TECHNIQUES = ["Indicator Removal from Tools","Windows Management Instrumentation",".bash_profile and .bashrc","Screen Capture","Bootkit","Logon Scripts","System Owner/User Discovery","Credential Dumping","Execution through Module Load","Stored Data Manipulation","File System Permissions Weakness","LLMNR/NBT-NS Poisoning and Relay","Rootkit","Systemd Service","Audio Capture","External Remote Services","Component Firmware","Timestomp","Permission Groups Discovery","Email Collection","Rc.common","Data from Removable Media","Code Signing","Process Hollowing","SID-History Injection","Port Monitors","Spearphishing Link","Service Stop","Sudo Caching","Security Software Discovery","Taint Shared Content","Securityd Memory","Startup Items","Office Application Startup","Disabling Security Tools","Disk Structure Wipe","Credentials in Registry","Automated Collection","Clipboard Data","AppInit DLLs","System Service Discovery","Network Sniffing","Network Share Discovery","Peripheral Device Discovery","System Information Discovery","Standard Application Layer Protocol","Scheduled Task","Login Item","Browser Extensions","Execution through API","Service Registry Permissions Weakness","Indirect Command Execution","Custom Cryptographic Protocol","Replication Through Removable Media","Data from Local System","Deobfuscate/Decode Files or Information","Supply Chain Compromise","Exploit Public-Facing Application","Remote Access Tools","Multilayer Encryption","Masquerading","Process Injection","Port Knocking","Signed Binary Proxy Execution","DLL Search Order Hijacking","New Service","Application Window Discovery","Standard Cryptographic Protocol","Hypervisor","AppCert DLLs","Scheduled Transfer","Winlogon Helper DLL","Binary Padding","Remote Desktop Protocol","Authentication Package","Extra Window Memory Injection","Domain Generation Algorithms","Man in the Browser","Remote Services","DCShadow","File Deletion","Private Keys","Modify Registry","Defacement","AppleScript","Browser Bookmark Discovery","Image File Execution Options Injection","Rundll32","Modify Existing Service","Communication Through Removable Media","File Permissions Modification","Hooking","System Firmware","Change Default File Association","Regsvr32","Indicator Blocking","Redundant Access","Spearphishing Attachment","Kernel Modules and Extensions","Security Support Provider","LSASS Driver","Video Capture","Gatekeeper Bypass","Software Packing","System Network Configuration Discovery","SIP and Trust Provider Hijacking","Account Discovery","Connection Proxy","Command-Line Interface","Domain Trust Discovery","Distributed Component Object Model","Automated Exfiltration","Indicator Removal on Host","File and Directory Discovery","Application Shimming","CMSTP","Multi-hop Proxy","Data Staged","System Network Connections Discovery","Scripting","Shared Webroot","Virtualization/Sandbox Evasion","Web Service","Multi-Stage Channels","Execution Guardrails","User Execution","Control Panel Items","Process Discovery","Input Prompt","Exfiltration Over Command and Control Channel","Registry Run Keys / Startup Folder","Shortcut Modification","Multiband Communication","Component Object Model Hijacking","Accessibility Features","Exploitation for Credential Access","Exploitation of Remote Services","Keychain","Trusted Relationship","Account Manipulation","Mshta","Exfiltration Over Alternative Protocol","Pass the Ticket","Brute Force","Data Obfuscation","Data from Network Shared Drive","Valid Accounts","DLL Side-Loading","Exploitation for Privilege Escalation","Kerberoasting","Obfuscated Files or Information","Password Policy Discovery","Forced Authentication","Data Encrypted for Impact","Disk Content Wipe","Password Filter DLL","Data Compressed","Credentials in Files","Netsh Helper DLL","Input Capture","Exploitation for Client Execution","Local Job Scheduling","Web Shell","Process Doppelgänging","SSH Hijacking","Standard Non-Application Layer Protocol","Pass the Hash","Query Registry","Data Transfer Size Limits","Windows Remote Management","Path Interception","Endpoint Denial of Service","Uncommonly Used Port","BITS Jobs","Bypass User Account Control","Transmitted Data Manipulation","Data Encoding","Compile After Delivery","Compiled HTML File","Data from Information Repositories","Spearphishing via Service","Hardware Additions","Data Destruction","Install Root Certificate","Data Encrypted","Drive-by Compromise","Network Denial of Service","Hidden Files and Directories","Template Injection","Access Token Manipulation","Time Providers","Two-Factor Authentication Interception","Launch Agent","Create Account","Remote System Discovery","Network Service Scanning","Exfiltration Over Physical Medium","Remote File Copy","Windows Management Instrumentation Event Subscription","Launch Daemon","Group Policy Modification","XSL Script Processing","Dynamic Data Exchange","Fallback Channels","NTFS File Attributes","System Time Discovery","Service Execution","PowerShell","Inhibit System Recovery","Signed Script Proxy Execution","Custom Command and Control Protocol","Commonly Used Port","Exploitation for Defense Evasion","Trusted Developer Utilities","Windows Admin Shares"]


def predict_old(report_to_predict, post_processing_parameters):
	"""
	Predict tactics and techniques from a report in a txt file.
	"""

	# loading the models
	pipeline_tactics = joblib.load('Models/tactics.joblib')
	pipeline_techniques = joblib.load('Models/techniques.joblib')

	report = processing(pd.DataFrame([report_to_predict], columns = ['Text']))[TEXT_FEATURES]
	
	# predictions
	predprob_tactics = pipeline_tactics.decision_function(report)
	pred_tactics = pipeline_tactics.predict(report)

	predprob_techniques = pipeline_techniques.decision_function(report)
	pred_techniques = pipeline_techniques.predict(report)
	
	if post_processing_parameters[0] == "HN":
		# hanging node thresholds retrieval and hanging node performed on predictions if in parameters
		pred_techniques = hanging_node(pred_tactics, predprob_tactics, pred_techniques, predprob_techniques, post_processing_parameters[1][0], post_processing_parameters[1][1])
	elif post_processing_parameters[0] == "CP":
		# confidence propagation performed on prediction if in parameters
		pred_techniques, predprob_techniques = confidence_propagation(predprob_tactics, pred_techniques, predprob_techniques)
	
	return pred_tactics, predprob_tactics, pred_techniques, predprob_techniques


# In[29]:


text = """Adversaries may execute active reconnaissance scans to gather information that can be used during targeting. Active scans are those where the adversary probes victim infrastructure via network traffic, as opposed to other forms of reconnaissance that do not involve direct interaction.

Adversaries may perform different forms of active scanning depending on what information they seek to gather. These scans can also be performed in various ways, including using native features of network protocols such as ICMP.[1][2] Information from these scans may reveal opportunities for other forms of reconnaissance (ex: Search Open Websites/Domains or Search Open Technical Databases), establishing operational resources (ex: Develop Capabilities or Obtain Capabilities), and/or initial access (ex: External Remote Services or Exploit Public-Facing Application)."""


# In[33]:


pred_tactics_new, predprob_tactics_new, pred_techniques_new, predprob_techniques_new = predict_new(text, 'HN')
pred_tactics_old, predprob_tactics_old, pred_techniques_old, predprob_techniques_old = predict_old(text, 'HN')
print(pred_tactics_new)
print(predprob_tactics_new)
print(pred_techniques_new)
print(predprob_techniques_new)


# In[31]:


print('[⚔️ NEW TACTICS]')
for i, tact in enumerate(pred_tactics_new[0]):
    if tact == 1:
        print(f'\t{NAME_TACTICS[i]}: {predprob_tactics_new[0][i]}')

print('[⚔️ NEW TACTICS]')
for i, tact in enumerate(pred_techniques_new[0]):
    if tact == 1:
        print(f'\t{NAME_TECHNIQUES[i]}: {predprob_techniques_new[0][i]}')

print('\n[⚔️ OLD TACTICS]')
for i, tact in enumerate(pred_tactics_old[0]):
    if tact == 1:
        print(f'\t{OLD_NAME_TACTICS[i]}: {predprob_tactics_old[0][i]}')

print('[⚔️ OLD TECHNIQUES]')
for i, tech in enumerate(pred_techniques_old[0]):
    if tech == 1:
        print(f'\t{OLD_NAME_TECHNIQUES[i]}: {predprob_techniques_old[0][i]}')

