Core Commands
=============

**Geheimnis** is a project consisting of several subprojects, that shall eventually made up an embedded system.
The system, including software and hardware, shall be able to connect to a PC via RJ45 or USB port, and is accessible to PC like a website providing HTTPS accessibility.
Either a user using his browser, or a software on PC using API to submit requests to this tiny website. Requests include, importing new _Contacts_/_Keys_/_Signatures_, requesting to encrypt/decrypt texts, etc. The software on this tiny hardware displays confirmation of such requests, then proceed and send out responds. Therefore, we say this project aimed at developing a device, that helps computer users authenticating, encrypting their communications. This device may also be a part of some kind of further systems, and helps automatically, e.g. for a system that controllling the entrance.

Introduction to this Subproject
-------------------------------

This subproject, called **Core Commands**, includes commands that run independently and do basic jobs like encrypting with given passphrase, decrypting with given passphrase, generic signing with given private key and plaintext, etc.

The data formats used in our whole project is different from any international standards. However, we will document that. Documentation shall also be another subproject.
