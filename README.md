python3 sort_images.py --eadir-remove ~/0_NAS_photo/backaup_pavel_telefon/ ~/0_NAS_photo/

#
sudo cp /home/paja/git/sort-images/sort-images.service /etc/systemd/system/
sudo cp /home/paja/git/sort-images/run_sort.sh /etc/systemd/system/  
# Or place it in a system path like /usr/local/bin/

sudo systemctl daemon-reload

sudo systemctl enable sort-images.service

sudo systemctl start sort-images.service

sudo systemctl status sort-images.service

The service requires the `/mnt/photo` mount and waits for it before starting.
It then waits 10 seconds before sorting, to allow the NAS to settle.