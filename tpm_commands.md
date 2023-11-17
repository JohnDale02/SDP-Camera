sudo apt-get update
sudo apt-get install tpm2-tools

tpm2_createprimary -C e -c primary.ctx
tpm2_create -G rsa -u rsa.pub -r rsa.priv -C primary.ctx
tpm2_load -C primary.ctx -u rsa.pub -r rsa.priv -n key.ctx
tpm2_evictcontrol -C o -c key.ctx 0x81010001  # make the key persistent

tpm2_sign -c 0x81010001 -g sha256 -o signature.bin hashfile  # used to sign hashdata file using key.ctx and save it to signature.bin

sudo tpm2_getcap handles-persistent  # used to show the persistent objects / keys

