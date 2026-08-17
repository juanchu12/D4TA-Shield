<?php

namespace App\Enum;

enum ContractStatus: string
{
    case Pending = 'pendiente';
    case InReview = 'en_revision';
    case Resolved = 'resuelto';
    case Failed = 'failed';
}
