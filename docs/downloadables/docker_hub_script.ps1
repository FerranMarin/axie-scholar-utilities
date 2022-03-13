# Alias to generate secrets
function axie-utils-gen-secrets {
    docker run -it -v $pwd\payments.json:/opt/app/files/payments.json -v $pwd\secrets.json:/opt/app/files/secrets.json epith/axie-scholar-utilities generate_secrets files/payments.json files/secrets.json
}
# Alias to managed generate secrets
function axie-utils-managed-gen-secrets {
    docker run -it -v $pwd\secrets.json:/opt/app/files/secrets.json epith/axie-scholar-utilities managed_generate_secrets files/secrets.json $token
}
# Alias to generate payments
function axie-utils-gen-payments {
    docker run -it -v $pwd\payments.csv:/opt/app/files/payments.csv -v $pwd\payments.json:/opt/app/files/payments.json epith/axie-scholar-utilities generate_payments files/payments.csv files/payments.json
}
# Alias to mass update secrets
function axie-utils-mass-update {
    docker run -it -v $pwd\update.csv:/opt/app/files/update.csv -v $pwd\secrets.json:/opt/app/files/secrets.json epith/axie-scholar-utilities mass_update_secrets files/update.csv files/secrets.json
}
# Alias to execute claims
function axie-utils-claim {
    docker run -it -v $pwd\payments.json:/opt/app/files/payments.json -v $pwd\secrets.json:/opt/app/files/secrets.json -v $pwd\logs:/opt/app/logs epith/axie-scholar-utilities claim files/payments.json files/secrets.json
}
# Alias to managed execute claims
function axie-utils-managed-claim {
    docker run -it -v $pwd\secrets.json:/opt/app/files/secrets.json -v $pwd\logs:/opt/app/logs epith/axie-scholar-utilities managed_claim files/secrets.json $token 
}
# Alias to execute payments
function axie-utils-payout {
    docker run -it -v $pwd\payments.json:/opt/app/files/payments.json  -v $pwd\secrets.json:/opt/app/files/secrets.json -v $pwd\logs:/opt/app/logs epith/axie-scholar-utilities payout files/payments.json files/secrets.json
}
# Alias to managed execute payments
function axie-utils-managed-payout {
    docker run -it -v $pwd\secrets.json:/opt/app/files/secrets.json -v $pwd\logs:/opt/app/logs epith/axie-scholar-utilities managed_payout files/secrets.json $token
}
# Alias to execute auto-payments (no confirmation)
function axie-utils-auto-payout {
    docker run -it -v $pwd\payments.json:/opt/app/files/payments.json -v $pwd\secrets.json:/opt/app/files/secrets.json -v $pwd\logs:/opt/app/logs epith/axie-scholar-utilities payout files/payments.json files/secrets.json -y
}
# Alias to managed execute auto-payments (no confirmation)
function axie-utils-managed-auto-payout {
    docker run -it -v $pwd\secrets.json:/opt/app/files/secrets.json -v $pwd\logs:/opt/app/logs epith/axie-scholar-utilities managed_payout files/secrets.json $token -y
}
# Alias to execute axie transfers
function axie-utils-transfer-axies {
    docker run -it -v $pwd\transfers.json:/opt/app/files/transfers.json -v $pwd\secrets.json:/opt/app/files/secrets.json -v $pwd\logs:/opt/app/logs epith/axie-scholar-utilities transfer_axies files/transfers.json files/secrets.json
}
#Alias to generate transfers file
function axie-utils-gen-transfers {
    docker run -it -v $pwd\transfers.csv:/opt/app/files/transfers.csv -v $pwd\transfers.json:/opt/app/files/transfers.json epith/axie-scholar-utilities generate_transfer_axies files/transfers.csv files/transfers.json
}
# Alias to execute generate_qr
function axie-utils-gen-QR {
    docker run -it -v $pwd\payments.json:/opt/app/files/payments.json -v $pwd\secrets.json:/opt/app/files/secrets.json -v ${pwd}:/opt/app/files epith/axie-scholar-utilities generate_QR files/payments.json files/secrets.json
}
# Alias to managed execute generate_qr
function axie-utils-managed-gen-QR {
    docker run -it -v $pwd\secrets.json:/opt/app/files/secrets.json -v ${pwd}:/opt/app/files epith/axie-scholar-utilities managed_generate_QR files/secrets.json $token
}
#Alias to generate breedings file
function axie-utils-gen-breedings {
    docker run -it -v $pwd\breedings.csv:/opt/app/files/breedings.csv -v $pwd\breedings.json:/opt/app/files/breedings.json epith/axie-scholar-utilities generate_breedings files/breedings.csv files/breedings.json
}
# Alias to breed axies
function axie-utils-axie-breeding {
    docker run -it -v $pwd\breedings.json:/opt/app/files/breedings.json -v $pwd\secrets.json:/opt/app/files/secrets.json -v $pwd\logs:/opt/app/logs epith/axie-scholar-utilities axie_breeding files/breedings.json files/secrets.json
}
# Alias to morph axies by ronin addresses
function axie-utils-axie-morphing($ronin_list) {
    docker run -it -v $pwd\secrets.json:/opt/app/files/secrets.json -v $pwd\logs:/opt/app/logs epith/axie-scholar-utilities axie_morphing files/secrets.json $ronin_list
}



function validate_ronin_addresses($ronin_list, $i = 0) {

    if($i -ge $ronin_list.length) {
        return;
    }

    $ronin_address = $ronin_list[$i] -split ":"
    $type = $ronin_address[0]
    $address = $ronin_address[1]

    if($type -ne "ronin") {
        Throw "Address in position " + ($i + 1) + " is not a valid Ronin Address. It should start with 'ronin'."
    }

    if($address.length -ne 40) {
        Throw "Ronin Address in position " + ($i + 1) + " is not a valid Ronin Address. A ronin address should have 40 characters."
    }

    validate_ronin_addresses $ronin_list ($i + 1)
}


$running = 1

while ($running -ne 0) {

    $choice = -1

    Write-Host "====================================="
    Write-Host "             AXIE UTILS              "
    Write-Host "====================================="
    Write-Host "1. Generate Payments"
    Write-Host "2. Mass Update Secrets"
    Write-Host "3. Generate Secrets"
    Write-Host "4. Execute Claims"
    Write-Host "5. Execute Payments"
    Write-Host "6. Execute Auto-Payments"
    Write-Host "7. Generate Transfers File"
    Write-Host "8. Execute Transfer Axies"
    Write-Host "9. Generate QR Code"
    Write-Host "10. Generate Breedings File"
    Write-Host "11. Execute Breed Axies"
    Write-Host "12. Execute Morph Axies by Ronin Addresses"
    Write-Host "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    Write-Host "   Managed commands (if you have axie.management Token)"
    Write-Host "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    Write-Host "13. Managed Generate Secrets"
    Write-Host "14. Managed Execute Claims"
    Write-Host "15. Managed Execute Payments"
    Write-Host "16. Managed Execute Auto-PaymentsPayments"
    Write-Host "17. Managed Generate QR Code"
    Write-Host "0. Exit"
    Write-Host "====================================="
    $choice = Read-Host "Choose an option: "

    switch ($choice) {
        0 { $running = 0 }
        1 { 
            axie-utils-gen-payments
            pause
        }
        2 { 
            axie-utils-mass-update
            pause
        }
        3 { 
            axie-utils-gen-secrets
            pause
        }
        4 { 
            axie-utils-claim
            pause
        }
        5 { 
            axie-utils-payout
            pause
        }
        6 { 
            axie-utils-auto-payout
            pause
        }
        7 { 
            axie-utils-gen-transfers
            pause
        }
        8 { 
            axie-utils-transfer-axies
            pause
        }
        9 { 
            axie-utils-gen-QR
            pause
        }
        10 { 
            axie-utils-gen-breedings
            pause
        }
        11 { 
            axie-utils-axie-breeding
            pause
        }
        12 { 
            $ronin_list = Read-Host "Ronin Addresses list where axies to morph are (separate with a comma)"
            validate_ronin_addresses ($ronin_list -split ",")
            axie-utils-axie-morphing $ronin_list
            pause
        }
        13 {
            $token = Read-Host "Introduce Axie.management Token:"
            axie-utils-managed-gen-secrets $token
            pause
        }
        14 {
            $token = Read-Host "Introduce Axie.management Token:"
            axie-utils-managed-claim $token
            pause
        }
        15 {
            $token = Read-Host "Introduce Axie.management Token:"
            axie-utils-managed-payout
            pause
        }
        16 {
            $token = Read-Host "Introduce Axie.management Token:"
            axie-utils-managed-auto-payout
            pause
        }
        17 {
            $token = Read-Host "Introduce Axie.management Token:"
            axie-utils-managed-gen-QR
            pause
        }
    }
}
