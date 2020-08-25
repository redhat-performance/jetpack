sudo yum install pciutils -y
nvme_exist=`lspci -nn | grep "Non-Volatile memory controller"`
if [[ $? == 0 ]]
then
 address=`lspci -nn | grep "Non-Volatile memory controller" | awk '{ print $1 }'`
 vendor=`lspci -nn | grep "Non-Volatile memory controller" | awk '{ print $NF }' | tr -d [] | cut -d: -f1`
 product=`lspci -nn | grep "Non-Volatile memory controller" | awk '{ print $NF }' | tr -d [] | cut -d: -f2`
 echo "nvme supported :-)"
 echo "address: $address"
 echo "vendor_id: $vendor"
 echo "product_id: $product"
else
 echo "nvme not supported :-("
fi

