
sudo apt-get update
sudo apt-get install tpm2-tools

sudo openssl dgst -verify public_key.pem -keyform pem -sha256 -signature data.out.signed combined.file
sudo tpm2 sign -Q -c 0x81010001(or key.ctx if not persistent) -g sha256 -d digest.file -f plain -s rsassa -o data.out.signed
sudo tpm2 readpublic -Q -c key.ctx -f pem -o public_key.pem 
python3 hash.py 
sudo tpm2 load -C primary.ctx -u rsa.pub -r rsa.priv -c key.ctx
sudo tpm2 create -G rsa -u rsa.pub -r rsa.priv -C primary.ctx
sudo tpm2 createprimary -C e -c primary.ctx

tpm2_evictcontrol -C o -c key.ctx 0x81010001  # make the key persistent

sudo tpm2_getcap handles-persistent  # used to show the persistent objects / keys



## HELPING WITH LOCKED STATE
- check the state of the TPM (locked etc...) RUN THE FOLLOWING COMMANDS TO CHECK IF LOCKOUT == 1
        sudo tpm2_getcap -l
        sudo tpm2_startup --clear 
        sudo tpm2_getcap properties-variable   // more information

- clear lockout state
        sudo tpm2_dictionarylockout --clear-lockout

- if you want to update lockout settings, input the following
        sudo tpm2_dictionarylockout --setup-parameters --max-tries=40000000 --recovery-time=1 --lockout-recovery=1




