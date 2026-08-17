<?php

$dir = __DIR__.'/config/jwt';
if (!is_dir($dir) && !mkdir($dir, 0775, true) && !is_dir($dir)) {
    fwrite(STDERR, "Cannot create JWT directory\n");
    exit(1);
}

$pass = getenv('JWT_PASSPHRASE') ?: 'change_me_jwt_passphrase';
$res = openssl_pkey_new([
    'private_key_bits' => 4096,
    'private_key_type' => OPENSSL_KEYTYPE_RSA,
]);
if ($res === false) {
    fwrite(STDERR, "openssl_pkey_new failed\n");
    exit(1);
}

openssl_pkey_export($res, $priv, $pass);
$details = openssl_pkey_get_details($res);
file_put_contents($dir.'/private.pem', $priv);
file_put_contents($dir.'/public.pem', $details['key']);
echo "jwt keys written\n";
