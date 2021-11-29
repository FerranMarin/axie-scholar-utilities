# Alias to generate payments
function axie-utils-trezor_config {
    poetry run python trezor_axie_scholar_cli.py config_trezor payments.json trezor_config.json
}
# Alias to generate payments
function axie-utils-gen-payments {
    poetry run python trezor_axie_scholar_cli.py generate_payments payments.json payments.json
}
# Alias to execute claims
function axie-utils-claim {
    poetry run python trezor_axie_scholar_cli.py claim payments.json trezor_config.json
}
# Alias to execute payments
function axie-utils-payout {
    poetry run python trezor_axie_scholar_cli.py payout payments.json trezor_config.json
}
# Alias to execute auto-payments (no confirmation)
function axie-utils-auto-payout {
    poetry run python trezor_axie_scholar_cli.py payout payments.json trezor_config.json -y
}
# Alias to execute axie transfers
function axie-utils-transfer-axies {
    poetry run python trezor_axie_scholar_cli.py transfer_axies transfers.json trezor_config.json
}
#Alias to generate transfers file
function axie-utils-gen-transfers {
    poetry run python trezor_axie_scholar_cli.py generate_transfer_axies transfers.csv transfers.json
}
# Alias to execute generate_qr
function axie-utils-gen-QR {
    poetry run python trezor_axie_scholar_cli.py generate_QR payments.json trezor_config.json
}
#Alias to generate breedings file
function axie-utils-gen-breedings {
    poetry run python trezor_axie_scholar_cli.py generate_breedings breedings.csv breedings.json
}
# Alias to breed axies
function axie-utils-axie-breeding {
    poetry run python trezor_axie_scholar_cli.py axie_breeding breedsings.json trezor_config.json
}
# Alias to morph axies by ronin addresses
function axie-utils-axie-morphing($ronin_list) {
    poetry run python trezor_axie_scholar_cli.py axie_morphing trezor_config.json $ronin_list
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
    Write-Host "2. Generate Trezor Config"
    Write-Host "3. Execute Claims"
    Write-Host "4. Execute Payments"
    Write-Host "5. Execute Auto-Payments"
    Write-Host "6. Generate Transfers File"
    Write-Host "7. Execute Transfer Axies"
    Write-Host "8. Generate QR Code"
    Write-Host "9. Generate Breedings File"
    Write-Host "10. Execute Breed Axies"
    Write-Host "11. Execute Morph Axies by Ronin Addresses"
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
            axie-utils-trezor_config
            pause
        }
        3 { 
            axie-utils-claim
            pause
        }
        4 { 
            axie-utils-payout
            pause
        }
        5 { 
            axie-utils-auto-payout
            pause
        }
        6 { 
            axie-utils-gen-transfers
            pause
        }
        7 { 
            axie-utils-transfer-axies
            pause
        }
        8 { 
            axie-utils-gen-QR
            pause
        }
        9 { 
            axie-utils-gen-breedings
            pause
        }
        10 { 
            axie-utils-axie-breeding
            pause
        }
        11 { 
            $ronin_list = Read-Host "Ronin Addresses list where axies to morph are (separate with a comma)"
            validate_ronin_addresses ($ronin_list -split ",")
            axie-utils-axie-morphing $ronin_list
            pause
        }
    }
}
