from app.models import db, Supplier

class SupplierController:

    @staticmethod
    def get_all_suppliers():
        suppliers = Supplier.query.all()
        return {'success': True, 'suppliers': [s.to_dict() for s in suppliers]}

    @staticmethod
    def get_supplier_by_id(supplier_id):
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return {'success': False, 'message': 'Proveedor no encontrado'}
        return {'success': True, 'supplier': supplier.to_dict()}

    @staticmethod
    def create_supplier(name, contact_person=None, phone=None, email=None):
        if Supplier.query.filter_by(name=name).first():
            return {'success': False, 'message': 'Ya existe un proveedor con ese nombre'}
        if email and Supplier.query.filter_by(email=email).first():
            return {'success': False, 'message': 'Ya existe un proveedor con ese email'}

        new_supplier = Supplier(
            name=name,
            contact_person=contact_person,
            phone=phone,
            email=email
        )
        db.session.add(new_supplier)
        db.session.commit()
        return {'success': True, 'message': 'Proveedor creado exitosamente', 'supplier': new_supplier.to_dict()}

    @staticmethod
    def update_supplier(supplier_id, name=None, contact_person=None, phone=None, email=None):
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return {'success': False, 'message': 'Proveedor no encontrado'}

        if name:
            supplier.name = name
        if contact_person is not None:
            supplier.contact_person = contact_person
        if phone is not None:
            supplier.phone = phone
        if email is not None:
            if email and Supplier.query.filter(Supplier.email == email, Supplier.id != supplier_id).first():
                return {'success': False, 'message': 'Ya existe otro proveedor con ese email'}
            supplier.email = email

        db.session.commit()
        return {'success': True, 'message': 'Proveedor actualizado exitosamente', 'supplier': supplier.to_dict()}

    @staticmethod
    def delete_supplier(supplier_id):
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return {'success': False, 'message': 'Proveedor no encontrado'}
        # Opcional: Verificar si hay productos asociados antes de eliminar un proveedor
        if supplier.products:
            return {'success': False, 'message': 'No se puede eliminar el proveedor porque tiene productos asociados.'}

        db.session.delete(supplier)
        db.session.commit()
        return {'success': True, 'message': 'Proveedor eliminado exitosamente'}